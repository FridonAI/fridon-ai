import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, IsString } from 'class-validator';

export class PaymentBodyDto {
  @ApiProperty({
    example:
      '4UcEfkYziTjiRHy9xEiuJogDHGkNSZ74isv1WgeBcQBpvx2XMfP9bsczo95Vg6dLL2G341UDaSzZzLLXstxM6MTg',
  })
  @IsString()
  @IsNotEmpty()
  transactionId: string;

  @ApiProperty({ example: 'plugin_1' })
  @IsString()
  pluginId: string;
}

export class UserPluginsResponseDto {
  @ApiProperty({
    example: [{ id: 'plugin_1', expiresAt: '2022-01-01T00:00:00.000Z' }],
  })
  plugins: { id: string; expiresAt: string | null }[];
}
