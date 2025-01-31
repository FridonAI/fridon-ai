import { Body, Controller, Post } from '@nestjs/common';
import { ApiSecurity, ApiTags } from '@nestjs/swagger';
import {
  DataProviderRequestBodyDto,
  DataProviderResponseBodyDto,
} from './data-provider.dto';
import { DataProviderService } from './data-provider.service';
import { Auth, Role } from 'src/auth/decorators/auth.decorator';

@Controller('data')
@ApiTags('data')
export class DataProviderController {
  constructor(private readonly service: DataProviderService) {}

  @Post('/executor')
  @ApiSecurity('auth')
  @Auth(Role.Public)
  async get(
    @Body() body: DataProviderRequestBodyDto,
  ): Promise<DataProviderResponseBodyDto> {
    console.log('body', body);

    const data = await this.service.resolve(
      `${body.plugin}-${body.function}`,
      body.args,
    );

    return { data: data };
  }
}
