import { Controller, Logger } from '@nestjs/common';
import { EventPattern } from '@nestjs/microservices';
import { AiChatMessageResponseGeneratedDto } from './ai.dto';
import { EventsService } from 'src/events/events.service';
import { BaseDto } from '@lib/common';

const eventName = 'response_received';

export class ChatResponseGeneratedDto extends BaseDto<ChatResponseGeneratedDto> {
  chatId: string;
  message: string;
}

@Controller()
export class AiEventsController {
  private logger = new Logger(AiEventsController.name);
  constructor(private readonly eventsService: EventsService) {}

  @EventPattern(eventName)
  accumulate(event: AiChatMessageResponseGeneratedDto): void {
    this.logger.debug(
      `Received event[${eventName}] from AI: ${JSON.stringify(event, null, 2)}`,
    );
    this.logger.debug(
      `Sending response[${event.data.message}] to user[${event.user.walletId}]`,
    );
    this.eventsService.sendTo(
      event.user.walletId,
      'chat.response-generated',
      new ChatResponseGeneratedDto({
        message: event.data.message,
        chatId: event.chatId,
      }),
    );
  }
}
