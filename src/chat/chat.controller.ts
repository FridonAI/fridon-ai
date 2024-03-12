import { Controller, Get, Post } from '@nestjs/common';
import { ChatService } from './chat.service';
import {
  CreateChatMessageResponseDto,
  CreateChatResponseDto,
  GetChatResponseDto,
  GetChatsResponseDto,
} from './chat.dto';
import { ChatId } from './domain/chat-id.value-object';
import { ApiTags } from '@nestjs/swagger';
import { Auth } from '@lib/auth';

@Controller('chats')
@ApiTags('chat')
@Auth()
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Get()
  async getChats(): Promise<GetChatsResponseDto> {
    const res = await this.chatService.getChats();

    return new GetChatsResponseDto({
      chats: res.map((chat) => ({
        id: chat.id.value,
      })),
    });
  }

  @Post()
  async createChat(): Promise<CreateChatResponseDto> {
    const res = await this.chatService.createChat();

    return new CreateChatResponseDto({
      chatId: res.id.value,
    });
  }

  @Get(':chatId')
  async getChat(chatId: string): Promise<GetChatResponseDto> {
    const res = await this.chatService.getChat(new ChatId(chatId));

    return new GetChatResponseDto({
      messages: res.messages.map((message) => ({
        query: message.query,
        response: message.response,
      })),
    });
  }

  @Post(':chatId')
  async createChatMessage(
    chatId: string,
  ): Promise<CreateChatMessageResponseDto> {
    const res = await this.chatService.createChatMessage(new ChatId(chatId));

    return new CreateChatMessageResponseDto({
      messageId: res.id.value,
    });
  }
}
