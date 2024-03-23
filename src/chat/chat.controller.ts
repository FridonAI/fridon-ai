import { Body, Controller, Get, Param, Post } from '@nestjs/common';
import { ChatService } from './chat.service';
import {
  ChatIdDto,
  CreateChatMessageRequestDto,
  CreateChatMessageResponseDto,
  CreateChatResponseDto,
  GetChatResponseDto,
  GetChatsResponseDto,
} from './chat.dto';
import { ChatId } from './domain/chat-id.value-object';
import { ApiTags } from '@nestjs/swagger';
import { Auth, Wallet, WalletSession } from '@lib/auth';
import { TransactionListenerService } from 'src/blockchain/transaction-listener/transaction-listener.service';

@Controller('chats')
@ApiTags('chat')
@Auth()
export class ChatHttpController {
  constructor(
    private readonly chatService: ChatService,
    private readonly transactionListenerService: TransactionListenerService,
  ) {}

  @Get()
  async getChats(
    @Wallet() wallet: WalletSession,
  ): Promise<GetChatsResponseDto> {
    const res = await this.chatService.getChats(wallet.walletAddress);

    return new GetChatsResponseDto({
      chats: res.map((chat) => ({
        id: chat.id.value,
        title: chat.title ?? 'New Chat',
      })),
    });
  }

  @Post()
  async createChat(
    @Wallet() wallet: WalletSession,
  ): Promise<CreateChatResponseDto> {
    const res = await this.chatService.createChat(wallet.walletAddress);

    return new CreateChatResponseDto({
      chatId: res.id.value,
    });
  }

  @Get(':chatId')
  async getChat(@Param() params: ChatIdDto): Promise<GetChatResponseDto> {
    const res = await this.chatService.getChat(new ChatId(params.chatId));

    return new GetChatResponseDto({
      messages: res.messages.map((message) => ({
        content: message.content,
        messageType: message.messageType,
      })),
    });
  }

  @Post(':chatId')
  async createChatMessage(
    @Param() params: ChatIdDto,
    @Body() body: CreateChatMessageRequestDto,
    @Wallet() { walletAddress }: WalletSession,
  ): Promise<CreateChatMessageResponseDto> {
    const res = await this.chatService.createChatMessageQuery(
      new ChatId(params.chatId),
      walletAddress,
      body.message,
    );

    return new CreateChatMessageResponseDto({
      messageId: res.id.value,
    });
  }

  @Post(':chatId/transaction')
  async registerChatTransactionId(
    @Param() { chatId }: ChatIdDto,
    @Body() body: { transactionId: string },
  ): Promise<void> {
    await this.transactionListenerService.registerTransactionListener(
      body.transactionId,
      { chatId },
    );
  }
}
