---
title: "{{ replace .File.ContentBaseName `-` ` ` }}"
slug: "{{ .File.ContentBaseName }}"
description: "한 줄 소개 — 목록 카드와 검색 결과에 나옵니다."
date: {{ .Date }}
image: cover.png
categories: ["한식"]
tags: []
prepTime: ""
cookTime: ""
servings: ""
difficulty: "쉬움"
draft: true
---

## 재료

{{`{{< ingredients >}}`}}
주재료

- 재료 000g

양념

- 간장 1큰술
{{`{{< /ingredients >}}`}}

## 만드는 법

{{`{{< steps >}}`}}
1. 첫 번째 단계.
2. 두 번째 단계.
{{`{{< /steps >}}`}}

{{`{{< tip >}}`}}
- 알아두면 좋은 점.
{{`{{< /tip >}}`}}
