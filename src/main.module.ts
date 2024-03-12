import { Module } from '@nestjs/common';
import { ChatModule } from './chat/chat.module';
import { EventsModule } from './events/events.module';
import { AuthModule } from './auth/auth.module';

@Module({
  imports: [AuthModule, ChatModule, EventsModule],
})
export class AppModule {}
