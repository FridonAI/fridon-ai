import { IEvent } from '@nestjs/cqrs';

export class BaseEvent<T> implements IEvent {
  constructor(data: T) {
    Object.assign(this, data);
  }
}
