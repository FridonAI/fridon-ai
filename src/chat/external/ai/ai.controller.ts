import { Controller } from '@nestjs/common';
import { EventPattern } from '@nestjs/microservices';

@Controller()
export class AiEventsController {
  @EventPattern('response_received')
  accumulate(data: any): void {
    console.log('[AiEventsController]: Data Received', data);
  }
}
