import { BaseDto } from '@lib/common';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import { IsNotEmpty, IsNumber, IsOptional, Max, Min } from 'class-validator';

// Shared
export class ChatIdDto extends BaseDto<ChatIdDto> {
  @ApiProperty({ example: '11111111-1111-1111-1111-111111111111' })
  chatId: string;
}

// Get Chat
export class GetChatsResponseDto extends BaseDto<GetChatsResponseDto> {
  @ApiProperty({ example: [{ id: '11111111-1111-1111-1111-111111111111' }] })
  chats: { id: string; title: string }[];
}

export class GetChatResponseDto extends BaseDto<GetChatResponseDto> {
  @ApiProperty({
    example: [
      { id: 'id1', content: 'Hello', messageType: 'Query' },
      { id: 'id2', content: 'Hi', messageType: 'Response' },
      { id: 'id3', content: 'Hello', messageType: 'Query' },
      { id: 'id4', content: 'U blind my G?', messageType: 'Response' },
    ],
  })
  messages: {
    id: string;
    content: string;
    messageType: 'Query' | 'Response';
  }[];
}

export class GetChatsRequestDto extends BaseDto<GetChatsRequestDto> {
  @ApiPropertyOptional({ description: 'Number of results to return per page.' })
  @Min(1)
  @Max(101)
  @IsOptional()
  @IsNumber()
  @Transform((a) => Number(a.value))
  limit?: number;
}

export class GetChatsHistoryItemResponseDto extends BaseDto<GetChatsHistoryItemResponseDto> {
  @ApiProperty({
    example: { walletId: '11111111-1111-1111-1111-111111111111' },
  })
  walletId: string;

  @ApiProperty({ example: 1618225200000 })
  createdAt: number;

  @ApiProperty({ example: 1618225200000 })
  updatedAt: number;

  @ApiProperty({
    example: [
      {
        id: '11111111-1111-1111-1111-111111111111',
        content: 'Hello',
        messageType: 'Query',
        personality: 'Yoda',
        createdAt: 1618225200000,
        updatedAt: 1618225200000,
      },
    ],
  })
  messages: {
    id: string;
    content: string;
    messageType: string;
    personality: string | null;
    plugins: string[];
    createdAt: number;
    updatedAt: number;
  }[];
}

export class GetChatsHistoryResponseDto extends BaseDto<GetChatsHistoryResponseDto> {
  @ApiProperty({ type: GetChatsHistoryItemResponseDto, isArray: true })
  data: GetChatsHistoryItemResponseDto[];
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
  @IsNotEmpty()
  message: string;

  @ApiProperty({ example: 'Yoda' })
  @IsNotEmpty()
  personality: string;
}

// Create Chat Message Info
export class CreateChatMessageInfoRequestDto extends BaseDto<CreateChatMessageInfoRequestDto> {
  @ApiProperty({
    example:
      '4UcEfkYziTjiRHy9xEiuJogDHGkNSZ74isv1WgeBcQBpvx2XMfP9bsczo95Vg6dLL2G341UDaSzZzLLXstxM6MTg',
  })
  transactionId: string;

  @ApiProperty({ example: 'Yoda' })
  @IsNotEmpty()
  personality: string;
}

export class TransactionCanceledRequestDto {
  @ApiProperty({ example: 'User canceled the transaction' })
  message: string;

  @ApiProperty({ example: 'Yoda' })
  @IsNotEmpty()
  personality: string;
}
