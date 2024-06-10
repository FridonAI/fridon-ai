import { EventsHandler } from '@nestjs/cqrs';
import {
  TransactionCanceledEvent,
  TransactionConfirmedEvent,
  TransactionFailedEvent,
  TransactionSkippedEvent,
} from 'src/blockchain/events/transaction.event';
import { ChatService } from '../chat.service';
import { ChatId } from '../domain/chat-id.value-object';
import { TransactionType } from 'src/blockchain/transaction-listener/types';
import { LeaderBoardService } from '../leaderboard.service';

@EventsHandler(TransactionConfirmedEvent)
export class TransactionConfirmedHandler {
  constructor(
    private readonly chatService: ChatService,
    private readonly leaderboardService: LeaderBoardService,
  ) {}

  async handle(event: TransactionConfirmedEvent) {
    if (event.transactionType !== TransactionType.CHAT) return;

    await this.chatService.createChatMessageTransactionResponse(
      new ChatId(event.aux.chatId),
      `Transaction with id ${event.transactionId} Confirmed`,
      event.aux.personality,
    );

    await this.leaderboardService.updateScore({
      walletId: event.aux.walletId,
      transactionsMade: 1,
    });
  }
}

@EventsHandler(TransactionSkippedEvent)
export class TransactionSkippedHandler {
  constructor(private readonly chatService: ChatService) {}

  async handle(event: TransactionSkippedEvent) {
    if (event.transactionType !== TransactionType.CHAT) return;

    await this.chatService.createChatMessageTransactionResponse(
      new ChatId(event.aux.chatId),
      `Transaction with id ${event.transactionId} Skipped`,
      event.aux.personality,
    );
  }
}

@EventsHandler(TransactionFailedEvent)
export class TransactionFailedHandler {
  constructor(private readonly chatService: ChatService) {}

  async handle(event: TransactionFailedEvent) {
    if (event.transactionType !== TransactionType.CHAT) return;

    await this.chatService.createChatMessageTransactionResponse(
      new ChatId(event.aux.chatId),
      `Transaction with id ${event.transactionId} Failed`,
      event.aux.personality,
    );
  }
}

@EventsHandler(TransactionCanceledEvent)
export class TransactionCanceledHandler {
  constructor(private readonly chatService: ChatService) {}

  async handle(event: TransactionCanceledEvent) {
    if (event.transactionType !== TransactionType.CHAT) return;

    await this.chatService.createChatMessageTransactionResponse(
      new ChatId(event.aux.chatId),
      event.reason,
      event.aux.personality,
    );
  }
}
