package unluac.decompile;

import java.util.ArrayList;
import java.util.List;
import unluac.parse.LFunction;
import unluac.parse.LUpvalue;

/** Recover lexical storage boundaries explicitly recorded by CLOSE and TBC. */
final class StrippedScopes {
  private StrippedScopes() {}

  static Declaration[] declarations(LFunction function, Code code, Declaration[] outer) {
    List<Declaration> result = new ArrayList<Declaration>();
    for(Declaration declaration : outer) result.add(declaration);
    int[] covered = new int[function.maximumStackSize];
    for(int line = 1; line <= code.length; line++) {
      if(code.op(line) == Op.CLOSURE) {
        for(LUpvalue upvalue : function.functions[code.Bx(line)].upvalues) {
          int register = upvalue.idx;
          if(!upvalue.instack || register < function.numParams || covered[register] >= line) continue;
          int close = close(code, line + 1, register);
          if(close == -1) continue; // The function's existing local already has the right lifetime.
          int begin = line - 1;
          while(begin > 0 && !closes(code, begin, register)) {
            if(!code.isUpvalueDeclaration(begin) && code.register(begin) == register
                && !bypassed(code, begin, line)) break;
            begin--;
          }
          if(begin == 0 || closes(code, begin, register)) continue;
          close = scopeClose(code, begin, close, register);
          Declaration declaration = new Declaration("L" + register + "_" + function.level + "_scope" + begin, begin, close - 1);
          declaration.register = register;
          result.add(declaration);
          covered[register] = close - 1;
        }
      } else if(code.op(line) == Op.TBC) {
        int register = code.A(line);
        int close = close(code, line + 1, register);
        int end = close == -1 ? code.length + function.header.version.outerblockscopeadjustment.get() : close - 1;
        Declaration declaration = new Declaration("L" + register + "_" + function.level + "_close" + line, line, end);
        declaration.register = register;
        declaration.tbc = true;
        result.add(declaration);
        covered[register] = end;
      }
    }
    return result.toArray(new Declaration[result.size()]);
  }

  private static int close(Code code, int begin, int register) {
    for(int line = begin; line <= code.length; line++) {
      if(closes(code, line, register)) return line;
    }
    return -1;
  }

  private static boolean jump(Code code, int line) {
    Op op = code.op(line);
    return op == Op.JMP || op == Op.JMP52 || op == Op.JMP54;
  }

  private static boolean bypassed(Code code, int begin, int capture) {
    for(int line = 1; line < begin; line++) {
      if(jump(code, line) && code.target(line) > begin && code.target(line) <= capture) return true;
    }
    return false;
  }

  private static int scopeClose(Code code, int begin, int end, int register) {
    // A break can close an upvalue on just one branch. Follow the branch that
    // skips that close to recover the enclosing lexical lifetime as well.
    boolean changed;
    do {
      changed = false;
      for(int line = begin; line < end; line++) {
        if(jump(code, line) && code.target(line) > end && !closes(code, line, register)
            && (line == 1 || !closes(code, line - 1, register))) {
          int next = close(code, code.target(line), register);
          if(next > end) { end = next; changed = true; }
        }
      }
    } while(changed);
    return end;
  }

  private static boolean closes(Code code, int line, int register) {
    switch(code.op(line)) {
      case CLOSE: case CLOSE55: return code.A(line) <= register;
      case JMP52: return code.A(line) != 0 && code.A(line) - 1 <= register;
      default: return false;
    }
  }
}
