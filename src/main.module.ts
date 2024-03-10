import { Module } from '@nestjs/common';
import { ChatModule } from './chat/chat.module';
import { EventsModule } from './events/events.module';

@Module({
  imports: [ChatModule, EventsModule],
})
export class AppModule {}
