import {
  Body,
  Controller,
  Get,
  Param,
  Post,
  Query,
  UseGuards,
} from '@nestjs/common';
import { ChatService } from './chat.service';
import {
  ChatIdDto,
  CreateChatMessageInfoRequestDto,
  CreateChatMessageRequestDto,
  CreateChatMessageResponseDto,
  CreateChatResponseDto,
  GetChatResponseDto,
  GetChatsHistoryRequestDto,
  GetChatsHistoryResponseDto,
  GetChatsRequestDto,
  GetChatsResponseDto,
  GetNotificationResponseDto,
  RectangleDto,
  TransactionCanceledRequestDto,
} from './chat.dto';
import { ChatId } from './domain/chat-id.value-object';
import { ApiSecurity, ApiTags } from '@nestjs/swagger';
import { TransactionListenerService } from 'src/blockchain/transaction-listener/transaction-listener.service';
import { EventBus } from '@nestjs/cqrs';
import { TransactionCanceledEvent } from 'src/blockchain/events/transaction.event';
import { TransactionType } from 'src/blockchain/transaction-listener/types';
import { WalletThrottlerGuard } from '@lib/throttling';
import { Auth, Role } from 'src/auth/decorators/auth.decorator';
import { Claims } from 'src/auth/decorators/claims.decorator';

@Controller('chats')
@ApiTags('chat')
export class ChatHttpController {
  constructor(
    private readonly chatService: ChatService,
    private readonly transactionListenerService: TransactionListenerService,
    private readonly eventBus: EventBus,
  ) {}

  @Get()
  @ApiSecurity('auth')
  @Auth(Role.User)
  async getChats(
    @Claims('sub') walletAddress: string,
    @Query() query: GetChatsRequestDto,
  ): Promise<GetChatsResponseDto> {
    const res = await this.chatService.getChats(
      walletAddress,
      query.chatType ?? 'Regular',
    );

    return new GetChatsResponseDto({
      chats: res.map((chat) => ({
        id: chat.id.value,
        title: chat.title ?? 'New Chat',
        rectangle: chat.rectangle
          ? {
              id: chat.rectangle.id,
              coin: chat.rectangle.coin,
              startDate: chat.rectangle.startDate,
              endDate: chat.rectangle.endDate,
              startPrice: chat.rectangle.startPrice,
              endPrice: chat.rectangle.endPrice,
              interval: chat.rectangle.interval,
            }
          : undefined,
      })),
    });
  }

  @Get('/history')
  @ApiSecurity('auth')
  @Auth(Role.User)
  async getChatHistory(
    @Claims('sub') walletAddress: string,
    @Query() query: GetChatsHistoryRequestDto,
  ) {
    const res = await this.chatService.getChatHistory(
      walletAddress,
      query.limit ?? 100,
      query.chatType ?? 'Regular',
    );

    return new GetChatsHistoryResponseDto({
      data: res.map((chat) => ({
        walletId: chat.walletId,
        createdAt: chat.createdAt.getTime(),
        updatedAt: chat.updatedAt.getTime(),
        messages: chat.messages.map((m) => ({
          id: m.id,
          content: m.content,
          messageType: m.messageType,
          personality: m.personality,
          structuredContent: m.structuredData
            ? JSON.parse(m.structuredData)
            : null,
          plugins: m.plugins,
          createdAt: m.createdAt.getTime(),
          updatedAt: m.updatedAt.getTime(),
        })),
      })),
    });
  }

  @Get('/notifications')
  @ApiSecurity('auth')
  @Auth(Role.User)
  async getChatNotifications(@Claims('sub') walletAddress: string) {
    const res = await this.chatService.getChatNotifications(walletAddress);

    return new GetNotificationResponseDto({
      messages: res.messages
        .map((m) => {
          return {
            id: m.id,
            content: m.content,
            messageType: m.messageType,
            structuredContent: m.structuredData
              ? JSON.parse(m.structuredData)
              : null,
            date: m.date.toISOString(),
          };
        })
        .filter(Boolean) as GetNotificationResponseDto['messages'],
    });
  }

  @Post()
  @ApiSecurity('auth')
  @Auth(Role.User)
  async createChat(
    @Claims('sub') walletAddress: string,
    @Body() rectangle?: RectangleDto,
  ): Promise<CreateChatResponseDto> {
    const res = await this.chatService.createChat(
      walletAddress,
      rectangle && Object.keys(rectangle).length > 0
        ? {
            id: rectangle.id,
            symbol: rectangle.coin,
            startDate: new Date(rectangle.startDate * 1000),
            endDate: new Date(rectangle.endDate * 1000),
            startPrice: rectangle.startPrice,
            endPrice: rectangle.endPrice,
            interval: rectangle.interval,
          }
        : undefined,
    );

    return new CreateChatResponseDto({
      chatId: res.id.value,
    });
  }

  @Get(':chatId')
  @ApiSecurity('auth')
  @Auth(Role.User)
  async getChat(@Param() params: ChatIdDto): Promise<GetChatResponseDto> {
    const res = await this.chatService.getChat(new ChatId(params.chatId));

    return new GetChatResponseDto({
      messages: res.messages
        .map((m) => {
          if (m.messageType !== 'Query' && m.messageType !== 'Response')
            return null;

          return {
            id: m.id,
            content: m.content,
            messageType: m.messageType,
            structuredContent: m.structuredData
              ? JSON.parse(m.structuredData)
              : null,
          };
        })
        .filter(Boolean) as GetChatResponseDto['messages'],
    });
  }

  @UseGuards(WalletThrottlerGuard)
  @Post(':chatId')
  @ApiSecurity('auth')
  @Auth(Role.User)
  async createChatMessage(
    @Param() params: ChatIdDto,
    @Body() body: CreateChatMessageRequestDto,
    @Claims('sub') walletAddress: string,
  ): Promise<CreateChatMessageResponseDto> {
    const res = await this.chatService.createChatMessageQuery(
      new ChatId(params.chatId),
      walletAddress,
      body.message,
      body.personality,
    );

    return new CreateChatMessageResponseDto({ messageId: res.id.value });
  }

  @Post(':chatId/transaction')
  @ApiSecurity('auth')
  @Auth(Role.User)
  async registerChatTransactionId(
    @Param() { chatId }: ChatIdDto,
    @Body() body: CreateChatMessageInfoRequestDto,
  ): Promise<void> {
    await this.transactionListenerService.registerTransactionListener(
      body.transactionId,
      TransactionType.CHAT,
      { walletId: 'NaN', chatId, personality: body.personality },
    );
  }

  @Post(':chatId/transaction-cancel')
  @ApiSecurity('auth')
  @Auth(Role.User)
  async transactionCancel(
    @Param() { chatId }: ChatIdDto,
    @Body() body: TransactionCanceledRequestDto,
  ): Promise<void> {
    await this.eventBus.publish(
      new TransactionCanceledEvent({
        reason: body.message,
        transactionType: TransactionType.CHAT,
        aux: { walletId: 'NaN', chatId, personality: body.personality },
      }),
    );
  }
}
