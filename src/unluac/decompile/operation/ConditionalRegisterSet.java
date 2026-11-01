package unluac.decompile.operation;

import java.util.Arrays;
import java.util.List;
import unluac.decompile.Registers;
import unluac.decompile.block.Block;
import unluac.decompile.block.IfThenEndBlock;
import unluac.decompile.condition.Condition;
import unluac.decompile.condition.TestCondition;
import unluac.decompile.statement.Assignment;
import unluac.decompile.statement.Statement;
import unluac.parse.LFunction;

/** TESTSET copies its operand only on the taken edge, including false and nil. */
public final class ConditionalRegisterSet extends Operation {
  private final LFunction function;
  private final int target, source;
  private final boolean truthy;

  public ConditionalRegisterSet(LFunction function, int line, int target, int source, boolean truthy) {
    super(line);
    this.function = function;
    this.target = target;
    this.source = source;
    this.truthy = truthy;
  }

  @Override
  public List<Statement> process(Registers r, Block block) {
    Condition condition = new TestCondition(line, source);
    if(!truthy) condition = condition.inverse();
    IfThenEndBlock copy = new IfThenEndBlock(function, r, condition, line, line + 1);
    copy.addStatement(new Assignment(r.getTarget(target, line), r.getExpression(source, line), line));
    copy.resolve(r);
    return Arrays.<Statement>asList(copy);
  }
}
