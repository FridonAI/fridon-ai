import {
  ExecutionContext,
  UnauthorizedException,
  createParamDecorator,
} from '@nestjs/common';

export type ClaimsType = {
  clientSig: string;
  nonce: string;
  iss: string;
  sub: string;
  iat: number;
  exp: number;
  serverSig: string;
  userType?: string;
  factionId?: string;
  referrer?: string;
};

export const Claims = createParamDecorator(
  (
    data: keyof ClaimsType | undefined,
    ctx: ExecutionContext,
  ): ClaimsType | string | number => {
    const request = ctx.switchToHttp().getRequest();

    const claims = request.claims;

    if (!claims) throw new UnauthorizedException();

    return data ? claims?.[data] : claims;
  },
);

export const ClaimsOptional = createParamDecorator(
  (
    data: keyof ClaimsType | undefined,
    ctx: ExecutionContext,
  ): ClaimsType | string | number | null => {
    const request = ctx.switchToHttp().getRequest();

    const claims = request.claims;

    if (!claims) return null;

    return data ? claims?.[data] : claims;
  },
);
