import { BaseDto } from '@lib/common';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import { IsIn, IsNotEmpty, IsNumber, IsOptional, IsString, Max, Min } from 'class-validator';

// Shared
export class ChatIdDto extends BaseDto<ChatIdDto> {
  @ApiProperty({ example: '11111111-1111-1111-1111-111111111111' })
  chatId: string;
}

// Get Chat
export class GetChatsResponseDto extends BaseDto<GetChatsResponseDto> {
  @ApiProperty({ example: [{ id: '11111111-1111-1111-1111-111111111111' }] })
  chats: { id: string; title: string, rectangle?: RectangleDto }[];
}

export class RectangleDto extends BaseDto<RectangleDto> {
  @ApiProperty({ example: '11111111-1111-1111-1111-111111111111' })
  id: string;

  @ApiProperty({ example: 'AAPL' })
  coin: string;

  @ApiProperty({ example: 1714857600000 })
  startDate: number;

  @ApiProperty({ example: 1714857600000 })
  endDate: number;

  @ApiProperty({ example: 100 })
  startPrice: number;

  @ApiProperty({ example: 200 })
  endPrice: number;

  @ApiProperty({ example: '1h' })
  interval: string;
}

export class GetChatResponseDto extends BaseDto<GetChatResponseDto> {
  @ApiProperty({
    example: [
      {
        id: 'id1',
        content: 'Hello',
        messageType: 'Query',
        structuredContent: null,
      },
      {
        id: 'id2',
        content: 'Hi',
        messageType: 'Response',
        structuredContent: '[1,2]',
      },
      {
        id: 'id3',
        content: 'Hello',
        messageType: 'Query',
        structuredContent: null,
      },
      {
        id: 'id4',
        content: 'U blind my G?',
        messageType: 'Response',
        structuredContent: null,
      },
    ],
  })
  messages: {
    id: string;
    content: string;
    structuredContent: string | null;
    messageType: 'Query' | 'Response';
  }[];

  @ApiPropertyOptional({ type: RectangleDto })
  rectangle?: RectangleDto;
}

export class GetNotificationResponseDto extends BaseDto<GetNotificationResponseDto> {
  @ApiProperty({
    example: [
      {
        id: 'id1',
        content: 'Hello',
        messageType: 'Query',
        structuredContent: null,
      },
      {
        id: 'id2',
        content: 'Hi',
        messageType: 'Response',
        structuredContent: null,
      },
      {
        id: 'id3',
        content: 'Hello',
        messageType: 'Query',
        structuredContent: null,
      },
      {
        id: 'id4',
        content: 'U blind my G?',
        messageType: 'Response',
        structuredContent: null,
      },
    ],
  })
  messages: {
    id: string;
    content: string;
    structuredContent: string | null;
    messageType: 'Notification';
    date: string;
  }[];
}

export class GetChatsRequestDto extends BaseDto<GetChatsRequestDto> {
  @ApiPropertyOptional({
    description: 'Type of chat to filter by',
    enum: ['Regular', 'SuperChart'],
    default: 'Regular'
  })
  @IsOptional()
  @IsString()
  @IsIn(['Regular', 'SuperChart'])
  chatType?: 'Regular' | 'SuperChart' = 'Regular';
}

export class GetChatsHistoryRequestDto extends BaseDto<GetChatsHistoryRequestDto> {
  @ApiPropertyOptional({ description: 'Number of results to return per page.' })
  @Min(1)
  @Max(101)
  @IsOptional()
  @IsNumber()
  @Transform((a) => Number(a.value))
  limit?: number;

  @ApiPropertyOptional({
    description: 'Type of chat to filter by',
    enum: ['Regular', 'SuperChart'],
    default: 'Regular'
  })
  @IsOptional()
  @IsString()
  @IsIn(['Regular', 'SuperChart'])
  chatType?: 'Regular' | 'SuperChart' = 'Regular';
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
    structuredContent: string | null;
    plugins: string[];
    createdAt: number;
    updatedAt: number;
  }[];

  @ApiPropertyOptional({ type: RectangleDto })
  rectangle?: RectangleDto;
}

export class GetChatsHistoryResponseDto extends BaseDto<GetChatsHistoryResponseDto> {
  @ApiProperty({ type: GetChatsHistoryItemResponseDto, isArray: true })
  data: GetChatsHistoryItemResponseDto[];
}

export class CreateChatRequestDto extends BaseDto<CreateChatRequestDto> {
  @ApiPropertyOptional({ type: RectangleDto })
  rectangle?: RectangleDto;
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
