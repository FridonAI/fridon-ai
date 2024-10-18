import { Controller, Logger } from '@nestjs/common';
import { EventPattern } from '@nestjs/microservices';
import { AiChatMessageResponseGeneratedDto, AiScoreUpdatedDto } from './ai.dto';
import { EventsService } from 'src/events/events.service';
import { BaseDto } from '@lib/common';
import { randomUUID } from 'crypto';
import { ChatService } from 'src/chat/chat.service';
import { ChatId } from 'src/chat/domain/chat-id.value-object';
import { AiAdapter } from './ai.adapter';
import { LeaderBoardService } from 'src/chat/leaderboard.service';
import { ChatMessageId } from 'src/chat/domain/chat-message-id.value-object';
import { PluginsService } from 'src/plugins/plugins.service';

const eventName = 'response_received';

export class ChatResponseGeneratedMessageDto extends BaseDto<ChatResponseGeneratedMessageDto> {
  type: 'message';
  id: string;
  chatId: string;
  message: string;
  structuredMessages: string[];
}

export class ChatResponseGeneratedTransactionDto extends BaseDto<ChatResponseGeneratedTransactionDto> {
  type: 'transaction';
  id: string;
  chatId: string;
  transaction: number[];
}

@Controller()
export class AiEventsController {
  private logger = new Logger(AiEventsController.name);

  constructor(
    private readonly eventsService: EventsService,
    private readonly aiAdapter: AiAdapter,
    private readonly chatService: ChatService,
    private readonly leaderBoardService: LeaderBoardService,
    private readonly pluginsService: PluginsService,
  ) {}

  @EventPattern(eventName)
  async process(event: AiChatMessageResponseGeneratedDto): Promise<void> {
    console.log('event', JSON.stringify(event, null, 2));
    function replacer(key: string, value: any) {
      try {
        if (key === 'serialized_transaction') {
          return `[${value.slice(0, 2).join(', ')} ... (${value.length - 4} more) ... ${value
            .slice(-2)
            .join(', ')}]`;
        }
        return value;
      } catch (error) {
        return value;
      }
    }

    if (event.data.id) {
      await this.aiAdapter.setChatQueueId(
        new ChatId(event.chat_id),
        event.data.id,
      );
    }

    this.logger.debug(
      `Received event[${eventName}] from AI: ${JSON.stringify(event, replacer, 2)}`,
    );

    // Handle transaction
    if (event.data.serialized_transaction) {
      this.logger.debug(
        `Sending serializedTransaction[${event.data.serialized_transaction}] to user[${event.user.wallet_id}]`,
      );

      this.eventsService.sendTo(
        event.user.wallet_id,
        'chat.response-generated',
        new ChatResponseGeneratedTransactionDto({
          type: 'transaction',
          id: randomUUID(),
          transaction: event.data.serialized_transaction,
          chatId: event.chat_id,
        }),
      );
      return;
    }

    // Handle message
    if (event.data.message || event.data.structured_messages) {
      const { id } = await this.chatService.createChatMessageAiResponse(
        new ChatId(event.chat_id),
        event.data.messageId
          ? new ChatMessageId(event.data.messageId)
          : undefined,
        event.data,
        event.data.pluginsUsed ?? [],
      );

      this.logger.debug(
        `Sending message[${event.data.message}] to user[${event.user.wallet_id}]`,
      );

      this.eventsService.sendTo(
        event.user.wallet_id,
        'chat.response-generated',
        new ChatResponseGeneratedMessageDto({
          type: 'message',
          id: id.value,
          message: event.data.message ?? '',
          structuredMessages: event.data.structured_messages ?? [],
          chatId: event.chat_id,
        }),
      );
      return;
    }
  }

  @EventPattern('scores_updated')
  async scoreUpdatedEventHandler(event: AiScoreUpdatedDto): Promise<void> {
    this.logger.debug(
      `Received event[score_updated] from AI: ${JSON.stringify(event, null, 2)}`,
    );

    await this.leaderBoardService.updateScore({
      chatId: event.chatId,
      walletId: event.walletId,
      plugins: event.pluginsUsed,
      score: event.score,
    });

    // update pluginsUsed plugin owners scores by 1
    for (const pluginId of event.pluginsUsed) {
      const pluginOwner = this.pluginsService.getPluginOwner(pluginId);
      await this.leaderBoardService.updateScore({
        // chatId: event.chatId,
        walletId: pluginOwner,
        score: event.score / 5,
        myPluginsUsed: 1,
      });
    }
  }
}
