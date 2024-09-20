import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, IsString } from 'class-validator';

export class FollowMediasBodyRequestDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'bonk' })
  server: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty()
  walletId: string;
}

export class UnfollowMediasBodyRequestDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty({ example: 'bonk' })
  server: string;

  @IsString()
  @IsNotEmpty()
  @ApiProperty()
  walletId: string;
}

export class GetFollowedMediasParamsRequestDto {
  @IsString()
  @IsNotEmpty()
  @ApiProperty()
  walletId: string;
}

export class GetMediasResponseDto {
  @IsString()
  @ApiProperty()
  medias: string[];
}
