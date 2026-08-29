const fs = require("fs");
const path = require("path");

const source = path.join(__dirname, "..", "node_modules", "material-symbols");

const destination = path.join(
    __dirname,
    "..",
    "static",
    "vendor",
    "material-symbols",
);

fs.mkdirSync(destination, {
    recursive: true,
});

for (const file of fs.readdirSync(source)) {
    if (
        file.endsWith(".css") ||
        file.endsWith(".woff2") ||
        file.endsWith(".woff")
    ) {
        fs.copyFileSync(path.join(source, file), path.join(destination, file));

        console.log(`Copied ${file}`);
    }
}
