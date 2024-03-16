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

@Controller('chats')
@ApiTags('chat')
@Auth()
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Get()
  async getChats(
    @Wallet() wallet: WalletSession,
  ): Promise<GetChatsResponseDto> {
    const res = await this.chatService.getChats(wallet.walletAddress);

    return new GetChatsResponseDto({
      chats: res.map((chat) => ({
        id: chat.id.value,
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
  ): Promise<CreateChatMessageResponseDto> {
    const res = await this.chatService.createChatMessageQuery(
      new ChatId(params.chatId),
      body.message,
    );

    return new CreateChatMessageResponseDto({
      messageId: res.id.value,
    });
  }
}
