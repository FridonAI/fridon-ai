export class BaseDto<T> {
  constructor(data: T) {
    Object.assign(this, data);
  }
}
