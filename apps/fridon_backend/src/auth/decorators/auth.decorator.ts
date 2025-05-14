import {
  createParamDecorator,
  ExecutionContext,
  HttpException,
  HttpStatus,
} from '@nestjs/common';

export const GetUser = createParamDecorator(
  (data: unknown, ctx: ExecutionContext) => {
    data;
    const req = ctx.switchToHttp().getRequest();
    if (!req.user || !req.user.privyId) {
      throw new HttpException(
        'User Authentication failed',
        HttpStatus.UNAUTHORIZED,
      );
    }
    return req.user.user;
  },
);
