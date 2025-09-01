import argparse
import json
from src.management import db_logic, retry_logic

def main():
    parser = argparse.ArgumentParser(description="Ferramenta de gerenciamento de mensagens com erro.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Comando 'list'
    parser_list = subparsers.add_parser("list", help="Lista mensagens não resolvidas.")
    
    # Comando 'show'
    parser_show = subparsers.add_parser("show", help="Mostra os detalhes de uma mensagem específica.")
    parser_show.add_argument("id", type=str, help="O ID da mensagem no MongoDB.")

    # Comando 'retry'
    parser_retry = subparsers.add_parser("retry", help="Reenfileira uma mensagem para ser processada novamente.")
    parser_retry.add_argument("id", type=str, help="O ID da mensagem no MongoDB.")

    # Comando 'discard'
    parser_discard = subparsers.add_parser("discard", help="Marca uma mensagem como descartada.")
    parser_discard.add_argument("id", type=str, help="O ID da mensagem no MongoDB.")

    args = parser.parse_args()

    if args.command == "list":
        messages = db_logic.list_failed_messages()
        if not messages:
            print("Nenhuma mensagem com erro encontrada.")
            return
        print(f"{'ID':<26} {'Data do Erro':<22} {'Conteúdo (resumo)'}")
        print("-" * 80)
        for msg in messages:
            content = msg.get("original_message", {}).get("content", "")
            print(f"{str(msg['_id']):<26} {msg['failed_at'].strftime('%Y-%m-%d %H:%M:%S'):<22} {content[:30]}...")

    elif args.command == "show":
        message = db_logic.get_failed_message(args.id)
        if message:
            print(json.dumps(message, default=str, indent=2))
        else:
            print(f"Mensagem com ID {args.id} não encontrada.")

    elif args.command == "retry":
        message = db_logic.get_failed_message(args.id)
        if not message:
            print(f"Mensagem com ID {args.id} não encontrada.")
            return
        
        if retry_logic.requeue_message(message):
            db_logic.update_status(args.id, "retried")
            print(f"Mensagem {args.id} reenfileirada com sucesso.")
        else:
            print(f"Falha ao reenfileirar a mensagem {args.id}.")
            
    elif args.command == "discard":
        if db_logic.update_status(args.id, "discarded"):
            print(f"Mensagem {args.id} marcada como descartada.")
        else:
            print(f"Mensagem com ID {args.id} não encontrada ou já atualizada.")

if __name__ == "__main__":
    main()