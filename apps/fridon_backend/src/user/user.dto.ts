import { ApiProperty } from '@nestjs/swagger';
import { IsOptional, IsString } from 'class-validator';

export class PaymentBodyDto {
  @ApiProperty({
    example:
      '4UcEfkYziTjiRHy9xEiuJogDHGkNSZ74isv1WgeBcQBpvx2XMfP9bsczo95Vg6dLL2G341UDaSzZzLLXstxM6MTg',
  })
  @IsString()
  @IsOptional()
  transactionId?: string;

  @ApiProperty({ example: 'plugin_1' })
  @IsString()
  pluginId: string;
}

export class UserPluginsResponseDto {
  @ApiProperty({
    example: [
      {
        id: 'plugin_1',
        expiresAt: '2022-01-01T00:00:00.000Z',
        type: 'Purchased',
      },
    ],
  })
  plugins: {
    id: string;
    expiresAt: string | null;
    type: 'Purchased' | 'PurchaseInProgress';
  }[];
}
