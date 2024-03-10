import { ICommand } from '@nestjs/cqrs';

export class BaseCommand<T> implements ICommand {
  constructor(data: T) {
    Object.assign(this, data);
  }
}
