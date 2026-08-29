# 메타쿡 (recipes.metacog.co.kr)

계량과 조리 순서를 그대로 적어두는 한국어 레시피 사이트. Hugo + [Stack](https://github.com/CaiJimmy/hugo-theme-stack) 테마로 만들고 GitHub Pages로 배포합니다.

## 로컬에서 실행하기

```bash
git clone --recurse-submodules https://github.com/jeonck/recipe.git
cd recipe
hugo server
```

이미 클론한 저장소라면 테마 서브모듈부터 받아야 합니다.

```bash
git submodule update --init --recursive
```

Hugo는 **extended 0.157.0 이상**이 필요합니다 (테마 요구사항). SCSS는 Hugo extended에 내장된 컴파일러로 처리하므로 Dart Sass를 따로 설치할 필요는 없습니다.

## 레시피 추가하기

1. 뼈대를 만듭니다. `archetypes/recipes.md` 템플릿이 적용됩니다.

   ```bash
   hugo new content recipes/<slug>/index.md
   ```

   프런트매터는 다음과 같습니다.

   ```yaml
   ---
   title: "돼지고기 김치찌개"
   slug: "kimchi-jjigae"
   description: "한 줄 소개. 목록 카드와 검색 결과에 나옵니다."
   date: 2026-03-04
   image: cover.png
   categories: ["한식", "국·찌개"]     # 첫 번째 카테고리가 커버 이미지 색을 정합니다
   tags: ["김치", "돼지고기"]
   prepTime: "10분"
   cookTime: "25분"
   chillTime: "재우기 30분"           # 선택 — 재우기·불리기·냉장 시간
   fermentTime: "실온 1~2일"          # 선택 — 김치처럼 발효·숙성이 필요한 경우
   servings: "2인분"
   difficulty: "쉬움"                 # 쉬움 / 보통 / 어려움
   ---
   ```

   `prepTime`, `cookTime`, `chillTime`, `fermentTime`, `servings`, `difficulty`는 본문 위 요약 바와
   목록 카드의 칩으로 자동 렌더링됩니다. 없는 항목은 그냥 빠집니다.

2. 본문에서 쓸 수 있는 숏코드:

   ```markdown
   {{< ingredients >}}
   주재료

   - 배추김치 300g

   양념

   - 고춧가루 1큰술
   {{< /ingredients >}}

   {{< steps >}}
   1. 첫 번째 단계.
   2. 두 번째 단계.
   {{< /steps >}}

   {{< tip title="실패 없이" >}}
   - 알아두면 좋은 것.
   {{< /tip >}}
   ```

   `ingredients`에 `title="양념"`을 주면 제목 줄이 붙은 별도 박스가 됩니다.
   `steps` 안의 순서 목록은 번호가 붙은 카드로 그려집니다.

3. 커버 이미지를 생성합니다. 사진 대신 카테고리 팔레트를 쓴 플랫 일러스트가 만들어집니다.

   ```bash
   pip install Pillow
   python3 scripts/gen_covers.py            # cover.png가 없는 레시피만
   python3 scripts/gen_covers.py --force    # 전부 다시 생성
   ```

   같은 폴더 이름이면 항상 같은 그림이 나오므로 다시 돌려도 결과가 바뀌지 않습니다.
   새 카테고리를 쓸 때는 `scripts/gen_covers.py`의 `PALETTES`에 색을 추가하세요.

## 저장소 구조

```
config/_default/       사이트 설정 (hugo/params/menu/markup/related)
content/recipes/       레시피 (페이지 번들: index.md + cover.png)
content/categories/    카테고리 설명과 URL slug
content/page/          검색·소개·전체 목록 같은 단독 페이지
layouts/_partials/     테마 위에 얹은 오버라이드 (요약 바, 목록 카드 칩)
layouts/_shortcodes/   ingredients / steps / tip
assets/scss/custom.scss  테마가 마지막에 불러오는 커스텀 스타일
assets/img/            아바타·파비콘
scripts/               커버·브랜드 이미지 생성기
static/CNAME           커스텀 도메인
```

테마 스타일을 손볼 때는 `themes/` 안을 고치지 말고 `assets/scss/custom.scss`에 쓰세요.
테마는 서브모듈이라 수정분이 날아갑니다. 참고로 Stack은 `html { font-size: 62.5% }`를
쓰기 때문에 **1rem = 10px** 기준으로 값을 잡아야 합니다.

## 배포

`main`에 푸시하면 `.github/workflows/deploy.yml`이 Hugo로 빌드해 GitHub Pages에 올립니다.

처음 한 번은 저장소 **Settings → Pages**에서 직접 켜야 합니다. Actions의 `GITHUB_TOKEN`으로는
Pages 사이트를 새로 만들 수 없기 때문입니다.

1. **Source**를 `GitHub Actions`로 지정
2. **Custom domain**에 `recipes.metacog.co.kr` 입력 (저장소에는 `static/CNAME`으로도 들어 있습니다)
3. DNS가 확인되면 **Enforce HTTPS** 체크

이후로는 `main`에 푸시할 때마다 자동 배포됩니다. Actions 탭에서 수동 실행(workflow_dispatch)도 가능합니다.
