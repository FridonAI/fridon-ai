import { Injectable } from '@nestjs/common';
import { EventsGateway } from './events.gateway';

@Injectable()
export class EventsService {
  constructor(private readonly eventsGateway: EventsGateway) {}

  sendTo(walletId: string, event: string, data: any) {
    this.eventsGateway.sendTo(walletId, event, data);
  }
}
