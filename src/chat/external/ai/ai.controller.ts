import { Controller, Logger } from '@nestjs/common';
import { EventPattern } from '@nestjs/microservices';
import { AiChatMessageResponseGeneratedDto } from './ai.dto';
import { EventsService } from 'src/events/events.service';

const eventName = 'response_received';

@Controller()
export class AiEventsController {
  private logger = new Logger(AiEventsController.name);
  constructor(private readonly eventsService: EventsService) {}

  @EventPattern(eventName)
  accumulate(data: AiChatMessageResponseGeneratedDto): void {
    this.logger.debug(
      `Received event[${eventName}] from AI: ${JSON.stringify(data, null, 2)}`,
    );
    this.logger.debug(
      `Sending response[${data.data.message}] to user[${data.user.walletId}]`,
    );
    this.eventsService.sendTo(
      data.user.walletId,
      'chat.response-generated',
      data.data.message,
    );
  }
}
