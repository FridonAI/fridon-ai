import { ArgumentsHost, HttpException, Logger } from '@nestjs/common';
import { BaseExceptionFilter } from '@nestjs/core';

export class CustomBaseExceptionFilter extends BaseExceptionFilter {
  private readonly logger = new Logger(CustomBaseExceptionFilter.name);

  override catch(exception: any, host: ArgumentsHost) {
    if (exception instanceof HttpException) {
      this.logger.error(exception.message);
    }

    return super.catch(exception, host);
  }
}
