package unluac.decompile;

/** Keep open results as expressions, rather than truncating/padding them to stack slots. */
public final class StrippedResults {
  private StrippedResults() {}

  public static boolean openTable(Code code, int line) {
    switch(code.op(line)) {
      case SETLISTO: return true;
      case SETLIST: case SETLIST52: case SETLIST54: return code.B(line) == 0;
      default: return false;
    }
  }

  private static boolean produces(Code code, int line) {
    switch(code.op(line)) {
      case CALL: case VARARG54: return code.C(line) == 0;
      case VARARG: return code.B(line) == 0;
      default: return false;
    }
  }

  private static boolean consumes(Code code, int line, int first) {
    if(openTable(code, line)) return code.A(line) < first;
    switch(code.op(line)) {
      case CALL: case TAILCALL: case TAILCALL54:
        return code.B(line) == 0 && code.A(line) < first;
      case RETURN: case RETURN54:
        return code.B(line) == 0 && code.A(line) <= first;
      default: return false;
    }
  }

  public static void configure(Code code, Registers r) {
    int[] entries = new int[code.length + 1];
    for(int line = 1; line <= code.length; line++) {
      for(OperandFormat operand : code.op(line).operands) {
        if(operand.format == OperandFormat.Format.JUMP || operand.format == OperandFormat.Format.JUMP_NEGATIVE) {
          int target = code.target(line);
          if(target > 0 && target <= code.length) entries[target]++;
        }
      }
    }
    for(int line = 1; line <= code.length; line++) entries[line] += entries[line - 1];
    for(int line = 1; line <= code.length; line++) {
      if(produces(code, line)) {
        if(line == code.length || !consumes(code, line + 1, code.A(line))
            || entries[line + 1] != entries[line]) {
          throw new IllegalStateException("Cannot reconstruct stripped open result consumer");
        }
        r.temporary(code.A(line), line, line);
      }
      if(openTable(code, line)) {
        int stack = code.A(line);
        int begin = line - 1;
        while(begin > 0 && line - begin <= 256 && !(code.A(begin) == stack && newTable(code.op(begin)))) begin--;
        if(begin == 0 || line - begin > 256 || entries[line] != entries[begin]
            || !constructor(code, begin, line, stack)) {
          throw new IllegalStateException("Cannot reconstruct stripped open table constructor");
        }
        r.temporary(stack, begin, line - 1);
        r.temporary(stack + 1, line, line);
      }
    }
  }

  private static boolean newTable(Op op) {
    return op == Op.NEWTABLE || op == Op.NEWTABLE50 || op == Op.NEWTABLE54;
  }

  private static boolean constructor(Code code, int begin, int end, int stack) {
    for(int line = begin + 1; line < end; line++) {
      Op op = code.op(line);
      switch(op) {
        case EXTRAARG: case EXTRABYTE: continue;
        case SETTABLE: case SETTABLE54: case SETI: case SETFIELD:
          if(code.A(line) < stack) return false;
          break;
        case MOVE: case LOADK: case LOADKX: case LOADI: case LOADF:
        case LOADNIL: case LOADNIL52: case GETUPVAL: case GETGLOBAL:
        case GETTABUP: case GETTABUP54: case GETTABLE: case GETTABLE54:
        case GETI: case GETFIELD: case NEWTABLE: case NEWTABLE50: case NEWTABLE54:
        case CALL:
          if(op == Op.CALL && (code.C(line) == 1 || code.C(line) > 2)) return false;
          if(code.A(line) <= stack) return false;
          break;
        case VARARG: case VARARG54:
          if(code.A(line) <= stack) return false;
          break;
        default: return false;
      }
      // The unfinished table must not escape or be observed before construction ends.
      for(OperandFormat operand : op.operands) {
        if(operand.field == OperandFormat.Field.A) continue;
        int value = code.field(operand.field, line);
        switch(operand.format) {
          case REGISTER: case REGISTER_K:
            if(value == stack) return false;
            break;
          case REGISTER_K54:
            if(!code.k(line) && value == stack) return false;
            break;
          default: break;
        }
      }
    }
    return true;
  }
}
