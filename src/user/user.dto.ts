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
  plugin: string;
}
