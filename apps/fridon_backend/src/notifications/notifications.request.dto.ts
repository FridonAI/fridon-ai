import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import {
  IsEnum,
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsString,
  Max,
  Min,
} from 'class-validator';
import { NotificationType } from './notifications.type';

// Alerts Request DTO
export class CreateAlertRequestDto {
  @ApiProperty({
    example: '52479f81-8d70-4e35-ab54-35d961f76a6e',
    description: 'Lesson Id',
  })
  @IsNotEmpty()
  @IsString()
  @Transform((param) => param?.value?.toLowerCase())
  readonly alertId: string;

  @ApiProperty({
    example: '',
    description: 'Wallet Id',
  })
  @IsNotEmpty()
  @IsString()
  readonly walletId: string;

  @ApiProperty({
    example: 'Notify me when the sol price is above 100',
    description: 'Alert message text',
  })
  @IsNotEmpty()
  @IsString()
  readonly text: string;
}

export class CreateNotificationRequestDto {
  @ApiProperty({
    example: '',
    description: 'Wallet Id',
  })
  @IsNotEmpty()
  @IsString()
  readonly walletId: string;

  @ApiProperty({
    example: NotificationType.Alert,
    type: 'string',
    enum: NotificationType,
    description: 'Notification type',
  })
  @IsEnum(NotificationType)
  readonly type: NotificationType;

  @ApiProperty({
    example: '',
    description: 'Message text',
  })
  @IsNotEmpty()
  @IsString()
  readonly text: string;
}

// Find Notifications Request DTO
export const availableSorts = ['createdAt'] as const;

export class FindNotificationsRequestDto {
  @ApiProperty({
    required: false,
    type: 'string',
    example: NotificationType.Alert,
    description: 'Tournament State Type',
  })
  @IsOptional()
  @IsEnum(NotificationType)
  readonly type?: NotificationType;

  @ApiProperty({
    example: true,
    description: 'Filter by unread notifications',
  })
  @IsOptional()
  readonly unread?: boolean;

  // Sort
  @ApiPropertyOptional({
    description: 'Sort by attribute',
    enum: availableSorts,
  })
  @IsOptional()
  @IsString()
  @IsEnum(availableSorts)
  sortBy?: (typeof availableSorts)[number];

  @ApiPropertyOptional({ description: 'Sort order', enum: ['asc', 'desc'] })
  @IsOptional()
  sortOrder?: 'asc' | 'desc';

  // Pagination
  @ApiPropertyOptional({ description: 'Number of results to return per page.' })
  @Min(1)
  @Max(50)
  @IsOptional()
  @IsNumber()
  @Transform((a) => Number(a.value))
  limit?: number;

  @ApiPropertyOptional({ description: 'Offset of the first result to return.' })
  @Min(1)
  @IsOptional()
  @IsNumber()
  @Transform((a) => Number(a.value))
  page?: number;
}
