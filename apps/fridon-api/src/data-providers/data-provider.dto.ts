import { ApiProperty } from '@nestjs/swagger';
import { IsObject, IsString } from 'class-validator';

// todo: change this
export class DataProviderRequestBodyDto {
  @IsString()
  @ApiProperty({ example: 'wallet' })
  plugin: string;

  @IsString()
  @ApiProperty({ example: 'transfer' })
  function: string;

  @IsObject()
  @ApiProperty({
    example: {
      walletAddress: 'Eurw43bfSFgvRBBy88f8jXQcSKekgBbXXcLmn5WoihZx',
      toAddress: '2vEN1J7AokPRq5xZvXqQinkv7RehHQN1hURR4xHJCkFB',
      currency: 'sol',
      amount: 0.1,
    },
  })
  args: object;
}

export class DataProviderResponseBodyDto {
  @IsString()
  data: object;
}
