import { Inject, Logger } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';
import { ChatId } from 'src/chat/domain/chat-id.value-object';
import { AiChatMessageCreatedDto, AiChatMessageInfoCreatedDto } from './ai.dto';
import { randomUUID } from 'crypto';
import { Redis } from 'ioredis';
import { Cache } from 'cache-manager';
import { CACHE_MANAGER } from '@nestjs/cache-manager';

export class AiAdapter {
  private logger = new Logger(AiAdapter.name);
  constructor(
    @Inject('AI_SERVICE') private client: ClientProxy,
    private readonly redis: Redis,
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
  ) {}

  emitChatMessageCreated(
    chatId: ChatId,
    messageId: string,
    walletId: string,
    message: string,
    personality: string,
    plugins: string[],
  ) {
    const eventName = 'chat_message_created';
    const event = new AiChatMessageCreatedDto({
      chatId: chatId.value,
      user: { walletId: walletId },
      data: { message, personality, messageId },
      plugins: plugins,
      aux: { traceId: randomUUID() },
    });

    this.logger.debug(
      `Emitting event[${eventName}] with data: ${JSON.stringify(event, null, 2)}`,
    );

    this.client.emit(eventName, event);
  }

  async emitChatMessageInfoCreated(chatId: ChatId, message: string) {
    const eventName = chatId.value;
    const event = new AiChatMessageInfoCreatedDto({
      chatId: chatId.value,
      user: { walletId: chatId.value },
      data: { message },
      aux: {
        traceId: randomUUID(),
      },
    });

    const queueId = await this.getChatQueueId(chatId);
    this.logger.debug(
      `Emitting event[${eventName}/${queueId}] with data: ${JSON.stringify(event, null, 2)}`,
    );

    this.client.emit(eventName, event);
    await this.redis.lpush(eventName, JSON.stringify(event));
    if (queueId) {
      await this.redis.lpush(queueId, JSON.stringify(event));
    } else {
      this.logger.warn(`QueueId not found for chatId: ${chatId.value}`);
    }
  }

  async getChatQueueId(chatId: ChatId): Promise<string | undefined> {
    return this.cacheManager.get<string>(this.getChatQueueIdKey(chatId));
  }

  async setChatQueueId(chatId: ChatId, queueId: string) {
    return this.cacheManager.set(
      this.getChatQueueIdKey(chatId),
      queueId,
      5 * 60 * 1000, // 5 minutes
    );
  }

  getChatQueueIdKey(chatId: ChatId) {
    return `chat-queue-id:${chatId.value}`;
  }
}
