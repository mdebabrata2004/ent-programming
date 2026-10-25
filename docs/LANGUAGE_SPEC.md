# ENT Language Specification

**Version:** 0.1.0  
**Language Name:** ENT  
**File Extension:** `.ent`

---

## 1. Introduction

ENT is a beginner-friendly, English-readable programming language designed primarily for website development.
ENT prioritizes readability, safety, and unambiguous deterministic syntax.

---

## 2. Core Syntax Rules

### 2.1 Program Delimiters
Every ENT program must be wrapped inside square brackets `[ ... ]`:

```ent
[
    say("Hello, World!")
]
```

Code written outside the outer brackets is rejected with a descriptive syntax error.

### 2.2 Forbidden Curly Braces
Curly braces `{ }` are **forbidden** in ENT syntax:

```ent
# INVALID - Will trigger a syntax error:
[
    if (age >= 18) {
        say("Adult")
    }
]

# VALID:
[
    if (age >= 18) [
        say("Adult")
    ]
]
```

### 2.3 Comments
ENT supports two comment styles:
- Hash comment: `# Comment text`
- Double-slash comment: `// Comment text`

Comments continue until the end of the line.

---

## 3. Data Types & Values

| Type | Examples | Description |
|---|---|---|
| **Number** | `42`, `-2`, `3.14` | Integer and floating-point numbers. |
| **String** | `"Hello"`, `'ENT'` | Double or single-quoted text. Supports standard escapes (`\n`, `\t`, `\"`, `\'`, `\\`). |
| **Boolean** | `true`, `false`, `yes`, `no` | Truth values. `yes` and `no` are synonyms for `true` and `false`. |
| **Nothing** | `nothing`, `none` | Represents the absence of a value (null/nil). |
| **List** | `[1, 2, 3]`, `["a", "b"]` | Ordered collection of ENT values. |

---

## 4. Variables & Assignment

Variables are defined using `remember(...)`:

```ent
[
    remember(name = "ENT")
    remember(version = "0.1.0", release_year = 2026)

    say("Welcome to " + name)
    say("Version: " + version)
]
```

Reassignment uses standard assignment syntax:

```ent
[
    remember(counter = 0)
    counter = counter + 1
    say(counter)
]
```

---

## 5. Expressions & Operators

### Arithmetic
- Addition / String Concatenation: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/` (checked for division by zero)
- Modulo: `%`

```ent
[
    say(2 + 2 - 9 + 3)   # Output: -2
    say("Age: " + 25)    # Output: Age: 25
]
```

### Comparison
- Equal: `==`
- Not Equal: `!=`
- Less Than: `<`
- Less or Equal: `<=`
- Greater Than: `>`
- Greater or Equal: `>=`

### Logical
- `and`: Short-circuiting logical AND
- `or`: Short-circuiting logical OR
- `not`: Logical negation

---

## 6. Control Flow

### Conditionals (`if / otherwise`)

```ent
[
    remember(score = 85)

    if (score >= 90) [
        say("Grade: A")
    ] otherwise if (score >= 80) [
        say("Grade: B")
    ] otherwise [
        say("Grade: C")
    ]
]
```

### Loops

#### Counted Repeat Loop
Bounded loop repeating a specified number of times:

```ent
[
    repeat (3 as i) [
        say("Index: " + i)
    ]
]
```

#### While Loop
Executes as long as the condition evaluates to true:

```ent
[
    remember(n = 3)
    while (n > 0) [
        say(n)
        n = n - 1
    ]
]
```

#### For-In Loop
Iterates over lists or characters in a string:

```ent
[
    for (fruit in ["apple", "banana", "cherry"]) [
        say(fruit)
    ]
]
```

---

## 7. Functions

User-defined functions use `function` (or alias `action`) and return values with `give` or `return`:

```ent
[
    function calculate_total(price, tax_rate) [
        remember(tax = price * tax_rate)
        give price + tax
    ]

    remember(final_price = calculate_total(100, 0.08))
    say("Total: $" + final_price)
]
```

Functions support lexical closures and recursion up to the configured safety depth.

---

## 8. Built-in Standard Library

No explicit imports are required for standard functions:

- **I/O**: `say(...)`
- **Conversion & Inspection**: `type_of(val)`, `to_number(val)`, `to_string(val)`, `to_bool(val)`
- **Math**: `round(n, decimals)`, `abs(n)`, `min(...vals)`, `max(...vals)`, `power(base, exp)`, `square_root(n)`
- **Strings**: `length(s)`, `uppercase(s)`, `lowercase(s)`, `trim(s)`, `contains(haystack, needle)`, `starts_with(s, prefix)`, `ends_with(s, suffix)`, `replace(s, old, new)`, `split(s, delim)`, `join(list, sep)`
- **Lists**: `push(list, item)`, `pop(list)`, `first(list)`, `last(list)`, `reverse(list)`, `range(start, end, step)`
