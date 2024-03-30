import { EventsHandler } from '@nestjs/cqrs';
import {
  TransactionConfirmedEvent,
  TransactionFailedEvent,
  TransactionSkippedEvent,
} from 'src/blockchain/events/transaction.event';
import { ChatService } from '../chat.service';
import { ChatId } from '../domain/chat-id.value-object';

@EventsHandler(TransactionConfirmedEvent)
export class TransactionConfirmedHandler {
  constructor(private readonly chatService: ChatService) {}

  async handle(event: TransactionConfirmedEvent) {
    await this.chatService.createChatMessageTransactionResponse(
      new ChatId(event.aux.chatId),
      'Transaction Confirmed',
      event.aux.narrator,
    );
  }
}

@EventsHandler(TransactionSkippedEvent)
export class TransactionSkippedHandler {
  constructor(private readonly chatService: ChatService) {}

  async handle(event: TransactionSkippedEvent) {
    await this.chatService.createChatMessageTransactionResponse(
      new ChatId(event.aux.chatId),
      'Transaction Skipped',
      event.aux.narrator,
    );
  }
}

@EventsHandler(TransactionFailedEvent)
export class TransactionFailedHandler {
  constructor(private readonly chatService: ChatService) {}

  async handle(event: TransactionFailedEvent) {
    await this.chatService.createChatMessageTransactionResponse(
      new ChatId(event.aux.chatId),
      'Transaction Failed',
      event.aux.narrator,
    );
  }
}
