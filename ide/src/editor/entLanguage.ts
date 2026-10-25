import type { Monaco } from '@monaco-editor/react';
import type { languages } from 'monaco-editor';

export const ENT_LANGUAGE_ID = 'ent';

export const entLanguageConfig: languages.LanguageConfiguration = {
  comments: {
    lineComment: '#',
  },
  brackets: [
    ['[', ']'],
    ['(', ')'],
  ],
  autoClosingPairs: [
    { open: '[', close: ']' },
    { open: '(', close: ')' },
    { open: '"', close: '"' },
    { open: "'", close: "'" },
  ],
  surroundingPairs: [
    { open: '[', close: ']' },
    { open: '(', close: ')' },
    { open: '"', close: '"' },
    { open: "'", close: "'" },
  ],
};

export const entTokensProvider: languages.IMonarchLanguage = {
  defaultToken: '',
  tokenPostfix: '.ent',

  keywords: [
    'remember',
    'if',
    'otherwise',
    'while',
    'repeat',
    'for',
    'in',
    'as',
    'function',
    'action',
    'return',
    'give',
    'and',
    'or',
    'not',
    'true',
    'false',
    'yes',
    'no',
    'nothing',
    'none',
  ],

  builtins: [
    'say',
    'page',
    'heading',
    'paragraph',
    'button',
    'link',
    'image',
    'style',
    'section',
    'container',
    'length',
    'type_of',
    'to_number',
    'to_string',
    'to_bool',
    'round',
    'abs',
    'min',
    'max',
    'power',
    'square_root',
    'uppercase',
    'lowercase',
    'trim',
    'split',
    'join',
    'contains',
    'replace',
    'push',
    'pop',
    'first',
    'last',
    'reverse',
    'range',
  ],

  operators: [
    '=',
    '+',
    '-',
    '*',
    '/',
    '%',
    '==',
    '!=',
    '<',
    '<=',
    '>',
    '>=',
  ],

  symbols: /[=><!~?:&|+\-*\/\^%]+/,

  tokenizer: {
    root: [
      // Identifiers & keywords
      [
        /[a-zA-Z_]\w*/,
        {
          cases: {
            '@keywords': 'keyword',
            '@builtins': 'predefined',
            '@default': 'identifier',
          },
        },
      ],

      // Whitespace & comments
      { include: '@whitespace' },

      // Delimiters and operators
      [/[\[\]\(\),;.]/, 'delimiter'],
      [
        /@symbols/,
        {
          cases: {
            '@operators': 'operator',
            '@default': '',
          },
        },
      ],

      // Numbers
      [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
      [/\d+/, 'number'],

      // Strings
      [/"([^"\\]|\\.)*$/, 'string.invalid'],
      [/"/, { token: 'string.quote', bracket: '@open', next: '@stringDouble' }],
      [/'([^'\\]|\\.)*$/, 'string.invalid'],
      [/'/, { token: 'string.quote', bracket: '@open', next: '@stringSingle' }],
    ],

    whitespace: [
      [/[ \t\r\n]+/, 'white'],
      [/#.*$/, 'comment'],
      [/\/\/.*$/, 'comment'],
    ],

    stringDouble: [
      [/[^\\"]+/, 'string'],
      [/\\./, 'string.escape'],
      [/"/, { token: 'string.quote', bracket: '@close', next: '@pop' }],
    ],

    stringSingle: [
      [/[^\\']+/, 'string'],
      [/\\./, 'string.escape'],
      [/'/, { token: 'string.quote', bracket: '@close', next: '@pop' }],
    ],
  },
};

export function registerEntLanguage(monaco: Monaco): void {
  // Only register once
  if (monaco.languages.getLanguages().some((l: { id: string }) => l.id === ENT_LANGUAGE_ID)) {
    return;
  }

  monaco.languages.register({ id: ENT_LANGUAGE_ID });
  monaco.languages.setLanguageConfiguration(ENT_LANGUAGE_ID, entLanguageConfig);
  monaco.languages.setMonarchTokensProvider(ENT_LANGUAGE_ID, entTokensProvider);

  monaco.languages.registerCompletionItemProvider(ENT_LANGUAGE_ID, {
    provideCompletionItems: (model: any, position: any) => {
      const word = model.getWordUntilPosition(position);
      const range = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn,
      };

      const suggestions = [
        // Keywords & snippets
        {
          label: 'remember',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'remember(${1:name} = ${2:value})',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Declares and stores a variable.',
          range,
        },
        {
          label: 'say',
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: 'say(${1:message})',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Prints output to standard console.',
          range,
        },
        {
          label: 'if',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'if (${1:condition}) [\n\t${2:say("True")}\n] otherwise [\n\t${3:say("False")}\n]',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Conditional statement with square brackets.',
          range,
        },
        {
          label: 'repeat',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'repeat (${1:count} as ${2:i}) [\n\t$0\n]',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Repeats code a bounded number of times.',
          range,
        },
        {
          label: 'while',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'while (${1:condition}) [\n\t$0\n]',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Executes loop while condition is true.',
          range,
        },
        {
          label: 'function',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'function ${1:name}(${2:parameters}) [\n\t$0\n\tgive ${3:result}\n]',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Declares a reusable ENT function.',
          range,
        },
        // Web builtins
        {
          label: 'page',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'page(title = "${1:My Website}") [\n\theading("${2:Welcome}")\n\tparagraph("${3:Hello, ENT!}")\n]',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Defines a static web page layout.',
          range,
        },
        {
          label: 'heading',
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: 'heading("${1:Text}", level = ${2:1})',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Renders an HTML heading tag (h1-h6).',
          range,
        },
        {
          label: 'paragraph',
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: 'paragraph("${1:Content}")',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Renders an HTML paragraph.',
          range,
        },
        {
          label: 'button',
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: 'button("${1:Label}")',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Renders an interactive button.',
          range,
        },
        {
          label: 'link',
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: 'link("${1:Text}", url = "${2:https://example.com}")',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Renders a secure hyperlink.',
          range,
        },
      ];

      return { suggestions };
    },
  });
}
