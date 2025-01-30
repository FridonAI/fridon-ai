import { Body, Controller, HttpStatus, Post } from '@nestjs/common';
import { CommandBus } from '@nestjs/cqrs';
import { ApiOperation, ApiResponse } from '@nestjs/swagger';
import { authRoutes } from '../../configs/app.routes';
import { SignInCommand } from './sign-in.command';
import { SignInRequestDto } from './sign-in.request';
import { SignInResponseDto } from './sign-in.response-dto';

@Controller(authRoutes.root)
export class SignInController {
  constructor(private commandBus: CommandBus) {}

  @Post(authRoutes.signIn)
  @ApiOperation({ summary: 'Sign In', tags: ['Auth'] })
  @ApiResponse({
    status: HttpStatus.CREATED,
    description: 'Sign In',
    type: SignInResponseDto,
  })
  @ApiResponse({
    status: HttpStatus.BAD_REQUEST,
    description: 'Validation failed',
  })
  public async create(
    @Body() body: SignInRequestDto,
  ): Promise<SignInResponseDto> {
    const { walletId, signature } = body;
    const token = await this.commandBus.execute(
      new SignInCommand(walletId, signature),
    );

    return new SignInResponseDto({
      token,
    });
  }
}
