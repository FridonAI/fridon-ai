import { DynamicModule, Module } from '@nestjs/common';
import { EventsGateway } from './events.gateway';
import { EventsService } from './events.service';

export interface EventsModuleOptions {
  isGlobal?: boolean;
}

@Module({
  providers: [EventsGateway, EventsService],
  exports: [EventsService],
})
export class EventsModule {
  static forRoot(options: EventsModuleOptions = {}): DynamicModule {
    return {
      global: options.isGlobal,
      module: EventsModule,
    };
  }
}
