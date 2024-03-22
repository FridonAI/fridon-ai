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

export class ChatResponseGeneratedDto extends BaseDto<ChatResponseGeneratedDto> {
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
    this.logger.debug(
      `Sending response[${event.data.message}] to user[${event.user.wallet_id}]`,
    );
    await this.chatRepository.createChatMessageResponse(
      new ChatId(event.chat_id),
      new ChatMessageId(randomUUID()),
      event.data.message,
    );
    this.eventsService.sendTo(
      event.user.wallet_id,
      'chat.response-generated',
      new ChatResponseGeneratedDto({
        message: event.data.message,
        chatId: event.chat_id,
      }),
    );
  }
}
