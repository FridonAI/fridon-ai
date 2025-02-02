import { Controller, Logger } from '@nestjs/common'
import { EventPattern } from '@nestjs/microservices'
import { BonkNotificationsMessageDto } from './bonk-notifications.dto'
import { PrismaService } from 'nestjs-prisma';
import { EventsService } from 'src/events/events.service';

@Controller()
export class BonkNotificationsController {
  private logger = new Logger(BonkNotificationsController.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly eventsService: EventsService,
  ) {}

  @EventPattern('bonk_notifier')
  async handleBonkNotifier(event: BonkNotificationsMessageDto) {
    console.log('event', JSON.stringify(event));
  }
}
