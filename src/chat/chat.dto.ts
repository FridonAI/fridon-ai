import { BaseDto } from '@lib/common';
import { ApiProperty } from '@nestjs/swagger';

// Shared
export class ChatIdDto extends BaseDto<ChatIdDto> {
  @ApiProperty({ example: '11111111-1111-1111-1111-111111111111' })
  chatId: string;
}

// Get Chat
export class GetChatsResponseDto extends BaseDto<GetChatsResponseDto> {
  @ApiProperty({ example: [{ id: '11111111-1111-1111-1111-111111111111' }] })
  chats: { id: string }[];
}

export class GetChatResponseDto extends BaseDto<GetChatResponseDto> {
  @ApiProperty({
    example: [
      { content: 'Hello' },
      { content: 'Hi, welcome to chat bot' },
      { content: 'Hello' },
      { content: 'U blind my G?' },
    ],
  })
  messages: { content: string }[];
}

// Create Chat
export class CreateChatResponseDto extends BaseDto<CreateChatResponseDto> {
  @ApiProperty({ example: '11111111-1111-1111-1111-111111111111' })
  chatId: string;
}

// Create Chat Message
export class CreateChatMessageResponseDto extends BaseDto<CreateChatMessageResponseDto> {
  @ApiProperty({ example: 'messageId' })
  messageId: string;
}

// Create Chat Message
export class CreateChatMessageRequestDto extends BaseDto<CreateChatMessageRequestDto> {
  @ApiProperty({ example: 'Hello, how are you?' })
  message: string;
}
