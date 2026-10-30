import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import unluac.Configuration;

/** Exercise the non-exiting library entry point repeatedly in one JVM. */
public final class Probe {
    public static void main(String[] args) throws Exception {
        try (BufferedReader input = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = input.readLine()) != null) {
                String[] fields = line.split("\t");
                Configuration config = new Configuration();
                config.variable = Configuration.VariableMode.valueOf(fields[0]);
                unluac.Main.decompile(fields[1], fields[2], config);
            }
        }
    }
}
