import { Body, Controller, HttpStatus, Post } from '@nestjs/common';
import { CommandBus } from '@nestjs/cqrs';
import { ApiOperation, ApiResponse } from '@nestjs/swagger';
import { authRoutes } from '../../configs/app.routes';
import { SignUpCommand } from './sign-up.command';
import { SignUpRequestDto } from './sign-up.request';

@Controller(authRoutes.root)
export class SignUpController {
  constructor(private commandBus: CommandBus) {}

  @Post(authRoutes.signUp)
  @ApiOperation({ summary: 'Sign Up', tags: ['Auth'] })
  @ApiResponse({
    status: HttpStatus.CREATED,
    description: 'Sign Up',
  })
  @ApiResponse({
    status: HttpStatus.BAD_REQUEST,
    description: 'Validation failed',
  })
  public async create(@Body() body: SignUpRequestDto) {
    const { walletId, signature } = body;
    await this.commandBus.execute(new SignUpCommand(walletId, signature));
  }
}
