import { Controller } from '@nestjs/common';
import { EventPattern } from '@nestjs/microservices';
import { AiChatMessageResponseGeneratedDto } from './ai.dto';
import { EventsService } from 'src/events/events.service';

@Controller()
export class AiEventsController {
  constructor(private readonly eventsService: EventsService) {}

  @EventPattern('response_received')
  accumulate(data: AiChatMessageResponseGeneratedDto): void {
    this.eventsService.sendTo(
      data.user.walletId,
      'chat.response-generated',
      data.data.message,
    );
  }
}
