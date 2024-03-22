import { Module } from '@nestjs/common';
import { ChatModule } from './chat/chat.module';
import { EventsModule } from './events/events.module';
import { AuthModule } from './auth/auth.module';
import { BlockchainModule } from './blockchain/blockchain.module';
import { ConfigModule } from '@nestjs/config';
import {
  PrismaModule,
  providePrismaClientExceptionFilter,
} from 'nestjs-prisma';
import { ScheduleModule } from '@nestjs/schedule';
import { CacheModule } from '@nestjs/cache-manager';
import { BullModule } from '@nestjs/bullmq';

@Module({
  imports: [
    // Nest Modules
    ConfigModule.forRoot({ isGlobal: true }),
    PrismaModule.forRoot({ isGlobal: true }),
    ScheduleModule.forRoot(),
    CacheModule.register({ isGlobal: true }),
    BullModule.registerQueue({
      name: 'transaction-listener',
      connection: {
        host: process.env['REDIS_HOST'],
      },
    }),

    // Custom Modules
    AuthModule,
    ChatModule,
    EventsModule.forRoot({ isGlobal: true }),
    BlockchainModule,
  ],
  providers: [providePrismaClientExceptionFilter()],
})
export class AppModule {}
