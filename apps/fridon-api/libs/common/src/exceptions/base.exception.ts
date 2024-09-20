export abstract class BaseException extends Error {
  static code: string;
  abstract get code(): string;
}

export function BaseExceptionCls(_code: string) {
  return class extends BaseException {
    static override code: string = _code;

    get code() {
      return _code;
    }
  };
}
