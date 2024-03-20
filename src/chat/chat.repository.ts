import { Injectable } from '@nestjs/common';
import { ChatId } from './domain/chat-id.value-object';
import { ChatMessageId } from './domain/chat-message-id.value-object';
import { PrismaService } from 'nestjs-prisma';

@Injectable()
export class ChatRepository {
  constructor(private readonly prisma: PrismaService) {}

  async getChats(walletId: string) {
    const chats = await this.prisma.chat.findMany({
      where: { walletId },
      include: { messages: { orderBy: { createdAt: 'asc' }, take: 1 } },
    });

    return chats;
  }

  async createChat(chatId: ChatId, walletId: string): Promise<void> {
    await this.prisma.chat.create({
      data: { id: chatId.value, walletId },
    });
  }

  async getChat(chatId: ChatId) {
    const chat = await this.prisma.chat.findUniqueOrThrow({
      where: { id: chatId.value },
      include: { messages: true },
    });

    return chat;
  }

  async createChatMessageQuery(
    chatId: ChatId,
    messageId: ChatMessageId,
    message: string,
  ): Promise<void> {
    await this.prisma.chatMessage.create({
      data: {
        id: messageId.value,
        chatId: chatId.value,
        content: message,
        messageType: 'Query',
      },
    });
  }

  async createChatMessageResponse(
    chatId: ChatId,
    messageId: ChatMessageId,
    message: string,
  ): Promise<void> {
    await this.prisma.chatMessage.create({
      data: {
        id: messageId.value,
        chatId: chatId.value,
        content: message,
        messageType: 'Response',
      },
    });
  }

  async createChatMessageQueryInfo(
    chatId: ChatId,
    messageId: ChatMessageId,
    data: object,
  ): Promise<void> {
    await this.prisma.chatMessage.create({
      data: {
        id: messageId.value,
        chatId: chatId.value,
        content: JSON.stringify(data),
        messageType: 'Response',
      },
    });
  }
}
