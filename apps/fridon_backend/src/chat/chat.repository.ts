import { Injectable } from '@nestjs/common';
import { ChatId } from './domain/chat-id.value-object';
import { PrismaService } from 'nestjs-prisma';
import { Prisma } from '@prisma/client';

@Injectable()
export class ChatRepository {
  constructor(private readonly prisma: PrismaService) {}

  async getChatNotifications(walletId: string) {
    const chatId = await this.prisma.chatNotifications.findUnique({
      where: { walletId },
    });

    if (!chatId) {
      return undefined;
    }

    const notificationChat = await this.prisma.chat.findUnique({
      where: {
        id: chatId.chatId,
      },
      include: {
        messages: {
          orderBy: { createdAt: 'desc' },
        },
      },
    });

    return notificationChat;
  }

  async getChats(walletId: string) {
    const chats = await this.prisma.chat.findMany({
      where: { walletId },
      include: { messages: { orderBy: { createdAt: 'asc' }, take: 1 } },
    });

    return chats;
  }

  async getChatHistory(walletId: string, limit: number) {
    const messages = await this.prisma.chatMessage.findMany({
      where: {
        Chat: {
          walletId: walletId,
        },
        messageType: 'Query',
      },
      orderBy: {
        createdAt: 'desc',
      },
      take: limit,
      include: {
        Chat: true,
      },
    });

    return messages;
  }

  async createChat(chatId: ChatId, walletId: string): Promise<void> {
    await this.prisma.chat.create({
      data: { id: chatId.value, walletId },
    });
  }

  async getChat(chatId: ChatId) {
    const chat = await this.prisma.chat.findUniqueOrThrow({
      where: { id: chatId.value },
      include: { messages: { orderBy: { createdAt: 'desc' } } },
    });

    return chat;
  }

  async createChatMessage(
    chatMessagePrisma: Prisma.ChatMessageCreateArgs['data'],
  ): Promise<void> {
    await this.prisma.chatMessage.create({ data: chatMessagePrisma });
  }

  async updateChatMessage(messageId: string, pluginsUsed: string[]) {
    await this.prisma.chatMessage.update({
      where: { id: messageId },
      data: {
        plugins: pluginsUsed,
      },
    });
  }
}
