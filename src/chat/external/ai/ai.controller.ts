import { Controller, Logger } from '@nestjs/common';
import { EventPattern } from '@nestjs/microservices';
import { AiChatMessageResponseGeneratedDto } from './ai.dto';
import { EventsService } from 'src/events/events.service';
import { BaseDto } from '@lib/common';
import { ChatRepository } from 'src/chat/chat.repository';
import { ChatId } from 'src/chat/domain/chat-id.value-object';
import { ChatMessageId } from 'src/chat/domain/chat-message-id.value-object';
import { randomUUID } from 'crypto';

const eventName = 'response_received';

export class ChatResponseGeneratedMessageDto extends BaseDto<ChatResponseGeneratedMessageDto> {
  type: 'message';
  id: string;
  chatId: string;
  transaction: number[];
}

export class ChatResponseGeneratedTransactionDto extends BaseDto<ChatResponseGeneratedTransactionDto> {
  type: 'message';
  id: string;
  chatId: string;
  message: string;
}

@Controller()
export class AiEventsController {
  private logger = new Logger(AiEventsController.name);

  constructor(
    private readonly eventsService: EventsService,
    private readonly chatRepository: ChatRepository,
  ) {}

  @EventPattern(eventName)
  async process(event: AiChatMessageResponseGeneratedDto): Promise<void> {
    this.logger.debug(
      `Received event[${eventName}] from AI: ${JSON.stringify(event, null, 2)}`,
    );
    const chatMessageId = new ChatMessageId(randomUUID());

    // Handle transaction
    if (event.data.serialized_transaction) {
      await this.chatRepository.createChatMessageResponse(
        new ChatId(event.chat_id),
        chatMessageId,
        JSON.stringify(event.data.serialized_transaction),
      );

      this.logger.debug(
        `Sending serializedTransaction[${event.data.serialized_transaction}] to user[${event.user.wallet_id}]`,
      );

      this.eventsService.sendTo(
        event.user.wallet_id,
        'chat.response-generated',
        new ChatResponseGeneratedMessageDto({
          type: 'message',
          id: chatMessageId.value,
          transaction: event.data.serialized_transaction,
          chatId: event.chat_id,
        }),
      );
    }

    // Handle message
    if (event.data.message) {
      await this.chatRepository.createChatMessageResponse(
        new ChatId(event.chat_id),
        chatMessageId,
        event.data.message,
      );

      this.logger.debug(
        `Sending message[${event.data.message}] to user[${event.user.wallet_id}]`,
      );

      this.eventsService.sendTo(
        event.user.wallet_id,
        'chat.response-generated',
        new ChatResponseGeneratedTransactionDto({
          type: 'message',
          id: chatMessageId.value,
          message: event.data.message,
          chatId: event.chat_id,
        }),
      );
    }
  }
}
