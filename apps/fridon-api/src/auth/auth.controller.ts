import { Body, Controller, Post } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { SignInDto } from './auth.dto';

@Controller('auth')
@ApiTags('auth')
export class AuthController {
  @Post('/sign-in')
  async signIn(@Body() body: SignInDto): Promise<{ token: string }> {
    return { token: body.walletAddress };
  }
}
