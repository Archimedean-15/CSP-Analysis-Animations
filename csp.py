from manim import *
from pathlib import Path
from transform_by_glyph_map import TransformByGlyphMap
from typing import Sequence, Callable

# accesses the SVGMobject at the specified index to determine if it's black or not
def get_b_k(cards: VGroup, k: int) -> int:
    if cards[k - 1][1].get_file_path().name[:1] == 'B':
        return 1
    return 0

def isBRInversion(cards: VGroup, i: int, j: int) -> bool:
    return get_b_k(cards, i) * (1 - get_b_k(cards, j)) == 1

def isBBPair(cards: VGroup, i: int, j: int) -> bool:
    return get_b_k(cards, i) * get_b_k(cards, j) == 1

def shuffle_cards(self, cards: VGroup, mappings: list) -> None:
    self.play(
        *[cards[i].animate.move_to(cards[mappings[i]].get_center()) for i in range(8)]
    )
    result = [None] * len(cards.submobjects)
    for i, new_index in enumerate(mappings):
        result[new_index] = cards[i]
    for i in range(len(result)):
        cards[i] = result[i]

def create_table(table: Sequence[Sequence[int]], col_labels: Sequence[int]) -> VGroup:
    int_table = IntegerTable(
        table, col_labels=col_labels,
        line_config={"stroke_width": 2}
    ).scale(0.55)
    int_table.remove(*int_table.get_vertical_lines())
    BB_table_labels = int_table.get_labels()
    for label in BB_table_labels:
        label.set_color(YELLOW).scale(1.1)

    rects = VGroup(
        *[SurroundingRectangle(int_table.get_rows()[i], buff=0.15, stroke_width=2) for i in range(1, len(int_table.get_rows()))]
    )

    return VGroup(int_table, rects)

def iterate_through_cards(
        self, expression_func: Callable[[VGroup, int, int], bool], cards: VGroup, \
        card_labels: VGroup, expression_tex: MathTex, sum_tracker: ValueTracker
) -> Sequence[Animation]:
    
    i_label = VGroup(MathTex("i"), Arrow(start=ORIGIN, end=DOWN)
    ).arrange(DOWN, buff=0.1).scale(0.6).next_to(card_labels[1], UP, buff=0.1
    ).set_color_by_gradient(RED, YELLOW_E)
    j_label = VGroup(MathTex("j"), Arrow(start=ORIGIN, end=DOWN)
    ).arrange(DOWN, buff=0.1).scale(0.6).next_to(card_labels[0], UP, buff=0.1
    ).set_color_by_gradient(BLUE_D, TEAL_D)

    create_arrows = [Create(i_label), Create(j_label)]
    # fence post case for starting position
    if(expression_func(cards, 2, 1)):
        expression_tex_equals_1 = MathTex(
            expression_tex.get_tex_string()[:-1] + "1"
        ).match_x(expression_tex)
        create_arrows.append(ReplacementTransform(expression_tex, expression_tex_equals_1))
        sum_tracker.increment_value(1)
        self.play(*create_arrows)
        self.replace(expression_tex_equals_1, expression_tex)
    else:
        self.play(*create_arrows)
    self.wait(0.2)
    
    for i in range(2, 8):
        if i <= 3:
            i_label.next_to(card_labels[i], UP, buff=0.1)
        else:
            if i == 4:
                i_label[1].rotate(PI)
                i_label.arrange(UP, buff=0.1)
            i_label.next_to(cards[i], DOWN, buff=0.1)
        self.add(i_label)

        for j in range(i):
            if j <= 3:
                j_label.next_to(card_labels[j], UP, buff=0.1)
            else:
                if j == 4:
                    j_label[1].rotate(PI)
                    j_label.arrange(UP, buff=0.1)
                j_label.next_to(cards[j], DOWN, buff=0.1)
            self.add(j_label)

            if(expression_func(cards, i + 1, j + 1)):
                self.play(sum_tracker.animate.increment_value(1), run_time=0.01)
            self.wait(0.2)
        
        if(j != 6):
            if(i >= 5):
                j_label[1].rotate(PI)
            j_label.arrange(DOWN, buff=0.1)
            j_label.next_to(card_labels[0], UP, buff=0.1)

    return [Uncreate(i_label), Uncreate(j_label)]


class CSP(Scene):

    def construct(self):

        ###---Setting up scene---###
        self.camera.background_color = GRAY_E


        ###---Putting all the SVG Cards into a VGroup---###
        folder = Path("SVG Cards")
        SVG_cards = sorted(
            p for p in folder.glob("*.svg")
        )

        cards = VGroup()
        for card in SVG_cards:
            card_mob = SVGMobject(file_name=card, stroke_width=0)
            rect = RoundedRectangle(corner_radius=0.3, 
                                    width=card_mob.width + 0.4, height=card_mob.height + 0.5,
                                    fill_color=WHITE, fill_opacity=1,
                                    stroke_width=0)
            cards.add(VGroup(rect, card_mob))

        cards.arrange_in_grid(rows=2, cols=4, buff=(MED_SMALL_BUFF, LARGE_BUFF))
        
        self.play(FadeIn(cards))
        self.wait(10)


        ###---Labels all of the cards---###
        card_labels = VGroup()
        for i in range(8):
            label = Tex(i+1).next_to(cards[i], UP)
            card_labels.add(label)

        self.play(ShowIncreasingSubsets(card_labels), run_time=1.5, rate_func=linear)
        self.wait(1)
        self.play(AnimationGroup(*[Indicate(card_labels[i]) for i in range(8)], lag_ratio=0.5))
        self.wait(1)


        ###---Creating definitions and setting boundaries---###
        self.play(VGroup(cards, card_labels).animate.scale(0.5).to_edge(LEFT, buff=0.5))
        b_k = MathTex(r"b_k", r"= \begin{cases} 1 & \text{card at position $k$ is black} \\ 0 & \text{card at position $k$ is red} \end{cases}"
                      ).to_edge(RIGHT)
        
        self.play(Write(b_k[0]))
        self.wait(0.25)
        self.play(Write(b_k[1]))
        self.wait(9)

        b_3 = MathTex("b_3 = 1").next_to(card_labels[3], UP, buff=0.5)
        b_3_arrow = CurvedArrow(b_3.get_corner(DL) + [0, -0.1, 0], cards[2].get_center() + [0, 0.25, 0], 
                                angle=-PI/4, stroke_color=BLUE_D, stroke_width=6)
        b_5 = MathTex("b_5 = 0").next_to(cards[7], DOWN, buff=0.75)
        b_5_arrow = CurvedArrow(b_5.get_corner(UL) + [-0.1, 0.1, 0], cards[6].get_center() - [0, 0.25, 0], 
                                angle=-PI/4, stroke_color=BLUE_D, stroke_width=6)

        self.play(Create(VGroup(b_3, b_3_arrow)))
        self.wait(0.8)
        self.play(Create(VGroup(b_5, b_5_arrow)))
        self.wait(2)
        self.play(Uncreate(VGroup(b_3, b_3_arrow, b_5, b_5_arrow)))
        self.wait(2)

        i_and_j = VGroup(
            MathTex(r"1 \leq i \leq 8"),
            MathTex(r"1 \leq j \leq 8"),
            MathTex(r"\Downarrow").scale(1.5),
            MathTex(r"1 \le j < i \le 8")
        ).arrange(DOWN).to_edge(DOWN, buff=1.5).match_x(b_k)
        self.play(AnimationGroup(
            b_k.animate.to_edge(UP, buff=1.5), Write(i_and_j[0]), Write(i_and_j[1]),
            lag_ratio=0.5
        ))
        self.wait(6)
        self.play(Write(i_and_j[2]), Write(i_and_j[3]))
        self.wait(7)


        ###---Setting up the mathematical expression---###
        starting_expression = MathTex("b_i", r"\left(1-b_j\right)").match_x(b_k)
        
        self.play(AnimationGroup(
            AnimationGroup(
                b_k.animate.scale(0.6).set_color(GRAY).to_edge(UP),
                i_and_j.animate.scale(0.6).set_color(GRAY).to_edge(DOWN)
            ), 
            Write(starting_expression), lag_ratio=0.5
        ))
        self.wait(4)
        self.play(Circumscribe(starting_expression[0]))
        self.wait(1.5)
        
        b_i = MathTex(r"b_i = \begin{cases} 1 & \text{card at position $i$ is black} \\ 0 & \text{card at position $i$ is red} \end{cases}")
        b_j = MathTex(r"b_j = \begin{cases} 1 & \text{card at position $j$ is black} \\ 0 & \text{card at position $j$ is red} \end{cases}")
        
        VGroup(b_i, b_j).arrange(DOWN).scale(0.75).match_x(b_k)

        self.play(AnimationGroup(starting_expression.animate.next_to(b_k, DOWN, buff=0.4),
                  Write(b_i), lag_ratio=0.5))
        self.wait(8)
        self.play(Circumscribe(starting_expression[1]))
        self.wait(1)
        b_i_copy = b_i.copy()
        self.play(b_i_copy.animate.next_to(b_i, DOWN),
                  ReplacementTransform(b_i_copy, b_j))
        self.wait(4)

        one_minus_b_j = MathTex(r"1-b_j = \begin{cases} 0 & \text{card at position $j$ is black} \\ 1 & \text{card at position $j$ is red} \end{cases}"
        ).match_y(b_j).match_height(b_j).align_to(b_j, LEFT)
        self.play(TransformByGlyphMap(b_j, one_minus_b_j, 
            ([], [0]), ([], [1]), *[([i], [i + 2]) for i in range(48)]
        ))
        self.wait(9)

        BR_table = create_table([[0, 0, 0],
                                [0, 1, 0],
                                [1, 0, 1],
                                [1, 1, 0]],
            col_labels=[MathTex(r"b_i"), MathTex(r"b_j"), 
                        MathTex(r"b_i\left(1-b_j\right)")]
        ).to_edge(RIGHT)
        
        self.play(AnimationGroup(
            VGroup(b_i, one_minus_b_j).animate.scale(0.65).next_to(cards, RIGHT),
            GrowFromCenter(BR_table[0]),
            lag_ratio=0.5
        ), run_time=1.5)    
        self.wait(4)

        BR_rects = BR_table[1]
        self.play(Create(BR_rects[2]))  
        self.wait(5)
        self.play(Uncreate(BR_rects[2]), Create(BR_rects[0]), 
                  Create(BR_rects[1]), Create(BR_rects[3]))
        self.wait(5)
        self.play(AnimationGroup(
            ShrinkToCenter(VGroup(b_i, one_minus_b_j, BR_table)),
            starting_expression.animate.set_y(0), lag_ratio=0.5
        ))
        self.wait(1.5)
        self.play(Indicate(i_and_j[3]), run_time=1.5)
        self.play(Swap(cards[3], cards[4]))
        self.wait(0.5)

        example_inversion = VGroup(
            MathTex(r"b_5\left(1-b_4\right)").match_x(starting_expression),
            MathTex(r"1\left(1-0\right) = 1").match_x(starting_expression)
        )
        example_inversion_arrow = CurvedArrow(
            starting_expression.get_edge_center(LEFT) + [-0.25, 0, 0],
            cards.get_edge_center(RIGHT) + [0.5, 0, 0], 
            angle=PI/4, stroke_color=BLUE_D, stroke_width=6
        )
        self.play(
            Write(example_inversion[0]),
            VGroup(starting_expression, example_inversion[0]
                   ).animate.arrange(DOWN).match_x(starting_expression),
            Create(example_inversion_arrow)
        )
        self.wait(0.5)
        self.play(
            Write(example_inversion[1]),
            VGroup(starting_expression, example_inversion[0], example_inversion[1]
                   ).animate.arrange(DOWN).match_x(starting_expression)
        )
        self.wait(4)
        self.play(
            AnimationGroup(
                AnimationGroup(
                    ShrinkToCenter(
                        VGroup(example_inversion_arrow, example_inversion)), Swap(cards[3], cards[4]
                    )
                ), starting_expression.animate.set_y(0), lag_ratio=0.5
            )
        )  
        self.wait(15)


        ###---Turning it into a sum---###
        starting_sum = MathTex(r"\sum_{i=1}^{8} \sum_{j=1}^{i-1} b_i \left(1-b_j\right)"
                               ).match_x(starting_expression) 
        starting_expression_temp = MathTex(
            r"b_i\left(1-b_j\right)"
        ).match_x(starting_expression).match_y(starting_expression)
        self.replace(starting_expression, starting_expression_temp)
        starting_expression = starting_expression_temp
        self.play(TransformByGlyphMap(
            starting_expression, starting_sum, 
            *[([], [i]) for i in range(12)], *[([i], [i + 12]) for i in range(8)]
        ))
        self.wait(2)
        
        sum_tracker = ValueTracker(0)
        starting_sum_equals_0_temp = MathTex(
            f"\\sum_{{i=1}}^{{8}} \\sum_{{j=1}}^{{i-1}} b_i \\left(1-b_j\\right) = 0"
        ).match_x(starting_sum)
        self.play(TransformByGlyphMap(
            starting_sum, starting_sum_equals_0_temp,
            *[([i], [i]) for i in range(20)], ([],[20]), ([],[21])
        ))
        
        starting_sum_equals_0 = always_redraw(lambda: MathTex(
            f"\\sum_{{i=1}}^{{8}} \\sum_{{j=1}}^{{i-1}} b_i \\left(1-b_j\\right) = {int(sum_tracker.get_value())}"
        ).match_x(starting_sum_equals_0_temp))
        #for some reason doing self.replace() doesn't work, so I just made it a very short animation
        self.play(ReplacementTransform(starting_sum_equals_0_temp, starting_sum_equals_0, run_time=0.01))

        # shuffles the cards "randomly"
        shuffle_cards(self, cards, [4, 6, 5, 1, 3, 0, 7, 2])

        uncreation = iterate_through_cards(self, isBRInversion, cards, card_labels, 
                                           starting_sum_equals_0, sum_tracker)
        uncreation.append(
            TransformByGlyphMap(starting_sum_equals_0, starting_sum,
            *[([i], [i]) for i in range(20)], ([20],[]), ([21],[]), ([22],[]))
        )
        self.wait(1)
        
        self.play(*uncreation)
        
        # returns the cards back to the solved state
        shuffle_cards(self, cards, [5, 3, 7, 4, 0, 2, 1, 6])


        ###---Rearranging the expression---###
        distribute_b_i = MathTex(r"\sum_{i=1}^{8} \sum_{j=1}^{i-1} b_i-b_i b_j"
                                ).match_x(starting_sum)
        self.play(TransformByGlyphMap(
            starting_sum, distribute_b_i, 
            *[([i], [i]) for i in range(12)], ([12],[12,15]), ([13],[13,16]), ([14,15],[]),
            ([16],[14]), ([17,18],[17,18]), ([19],[])
        ))
        
        og_split_into_separate_sums = MathTex(
            r"\sum_{i=1}^{8} \sum_{j=1}^{i-1} b_i- \sum_{i=1}^{8} \sum_{j=1}^{i-1}b_i b_j"
        ).match_x(distribute_b_i)
        og_split_into_separate_sums.save_state()
        self.play(TransformByGlyphMap(
            distribute_b_i, og_split_into_separate_sums,
            *[([i], [i,i+15]) for i in range(12)], ([12,13],[12,13]), ([14],[14]), 
            ([15,16],[27,28]), ([17,18],[29,30])
        ))
        split_into_separate_sums_temp = MathTex(
            r"\sum_{i=1}^{8} \sum_{j=1}^{i-1} b_i-", r"\sum_{i=1}^{8} \sum_{j=1}^{i-1}b_i b_j"
        ).match_x(og_split_into_separate_sums)
        #for some reason doing self.replace() doesn't work, so I just made it a very short animation
        self.play(ReplacementTransform(
            og_split_into_separate_sums, split_into_separate_sums_temp, run_time=0.01
        ))
        split_into_separate_sums = split_into_separate_sums_temp

        self.play(ShrinkToCenter(
            split_into_separate_sums[0]),
            split_into_separate_sums[1].animate.match_x(b_k)
        )
        
        BB_table = create_table([[0, 0, 0],
                                [0, 1, 0],
                                [1, 0, 0],
                                [1, 1, 1]],
                    col_labels=[MathTex(r"b_i"), MathTex(r"b_j"), 
                    MathTex(r"b_i b_j")]
        ).to_edge(RIGHT, buff=1.5)

        self.play(AnimationGroup(
            split_into_separate_sums[1].animate.set_x(cards.get_right()[0] + 2.5),
            GrowFromCenter(BB_table[0]),
            lag_ratio=0.5
        ), run_time=1.5)    

        BB_rects = BB_table[1]
        self.play(Create(BB_rects[0]), Create(BB_rects[1]), Create(BB_rects[2]))
        self.play(Uncreate(BB_rects[0]), Uncreate(BB_rects[1]), Uncreate(BB_rects[2]),
                  Create(BB_rects[3]))
        self.play(AnimationGroup(
            ShrinkToCenter(BB_table),
            split_into_separate_sums[1].animate.match_x(b_k), lag_ratio=0.5
        ))

        sum_tracker = ValueTracker(0)
        second_term = MathTex(
            f"\\sum_{{i=1}}^{{8}} \\sum_{{j=1}}^{{i-1}} b_i b_j"
        ).match_x(split_into_separate_sums[1])
        self.replace(split_into_separate_sums[1], second_term)
        second_term_equals_0_temp = MathTex(
            second_term.get_tex_string() + "= 0"
        ).match_x(second_term)
        self.play(TransformByGlyphMap(
            second_term, second_term_equals_0_temp,
            *[([i], [i]) for i in range(16)], ([],[16]), ([],[17])
        ))
    
        second_term_equals_0 = always_redraw(lambda: MathTex(
            f"\\sum_{{i=1}}^{{8}} \\sum_{{j=1}}^{{i-1}} b_i b_j = {int(sum_tracker.get_value())}"
        ).match_x(second_term_equals_0_temp))
        # for some reason doing self.replace() doesn't work, so I just made it a very short animation
        self.play(ReplacementTransform(second_term_equals_0_temp, second_term_equals_0, run_time=0.01))

        # shuffles the cards "randomly"
        shuffle_cards(self, cards, [6, 2, 5, 0, 7, 3, 1, 4])
        uncreation = iterate_through_cards(self, isBBPair, cards, card_labels, 
                                           second_term_equals_0, sum_tracker)
        four_choose_two = VGroup(
            MathTex(r"\binom{4}{2}").to_edge(RIGHT, buff=2).match_y(second_term_equals_0),
        )
        # added after the previous line so it could have the same x and y positions
        four_choose_two.add(
            MathTex(r"\binom{4}{2} = 6").match_x(four_choose_two[0]).match_y(four_choose_two[0])
        )
        uncreation.extend([
            second_term_equals_0.animate.set_x(cards.get_right()[0] + 3),
            Write(four_choose_two[0])
        ])
        second_term_equals_0.clear_updaters()
        self.wait(1)
        self.play(*uncreation)
        # returns the cards back to the solved state
        shuffle_cards(self, cards, [3, 6, 1, 5, 7, 2, 0, 4])

        self.play(TransformByGlyphMap(
            four_choose_two[0], four_choose_two[1],
            *[([i], [i]) for i in range(4)], ([],[4,5])
        ))

        equivalence = MathTex(r"\sum_{i=1}^{8} \sum_{j=1}^{i-1}b_i b_j = \binom{4}{2} = 6"
                              ).match_x(b_k)
        self.play(
            TransformByGlyphMap(
                second_term_equals_0, equivalence,
                *[([i], [i]) for i in range(16)], ([16],[16,21]), ([17],[22])
            ),
            TransformByGlyphMap(
                four_choose_two[1], equivalence,
                *[([i], [i + 17]) for i in range(6)]
            )
        )
        check_mark = SVGMobject("check_mark.svg").scale(0.4).next_to(equivalence, UP, buff=0.1)
        self.play(FadeIn(check_mark))
        self.wait(0.5)
        self.play(FadeOut(check_mark))

        og_split_into_separate_sums.restore().match_x(equivalence).shift(UP)

        first_term_minus_6_tex = r"\sum_{i=1}^{8} \sum_{j=1}^{i-1} b_i-6"
        first_term_minus_6 = MathTex(first_term_minus_6_tex
                                     ).align_to(split_into_separate_sums, LEFT)
        
        self.play(AnimationGroup(
            FadeOut(equivalence),
            AnimationGroup(FadeIn(og_split_into_separate_sums), og_split_into_separate_sums.animate.shift(DOWN)),
            lag_ratio=0.35
        ))

        self.play(TransformByGlyphMap(
            og_split_into_separate_sums, first_term_minus_6, 
            *[([i], [i]) for i in range(15)], *[([i], [15]) for i in range(15, 31)]
        ))

        mod_2 = MathTex(first_term_minus_6.get_tex_string() + r"\pmod{2}"
                        ).align_to(first_term_minus_6, LEFT)
        self.play(TransformByGlyphMap(
            first_term_minus_6, mod_2,
            *[([i], [i]) for i in range(16)], *[([], [i]) for i in range(16, 22)]
        ))

        minus_0 = MathTex(
            first_term_minus_6_tex[:first_term_minus_6_tex.index("6")] 
            + "0" + mod_2.get_tex_string()[-8:]
        ).align_to(mod_2, LEFT)
        self.play(TransformByGlyphMap(
            mod_2, minus_0,
            *[([i], [i]) for i in range(21)]
        ))

        first_term = MathTex(
            first_term_minus_6_tex[:first_term_minus_6_tex.index("-6")]
            + mod_2.get_tex_string()[-8:]
        ).align_to(minus_0, LEFT)
        self.play(TransformByGlyphMap(
            minus_0, first_term,
            *[([i], [i]) for i in range(14)], ([14,15],[]),
            *[([i], [i - 2]) for i in range(16, 21)]
        ))

        # flashes the i subscript on the b_i
        self.play(Flash(first_term[0][13]))
        first_term_temp = MathTex(
            first_term.get_tex_string()[:first_term.get_tex_string().index(r"\p")],
            first_term.get_tex_string()[first_term.get_tex_string().index(r"\p"):]
        ).move_to(first_term)
        self.play(ReplacementTransform(first_term, first_term_temp), run_time=0.01)
        first_term = first_term_temp
        
        expansion_tex = []
        for i in range(2, 9):
            expansion_tex.append(f"b_{i} +" * (i-1))
        # removes the final plus sign
        expansion_tex[-1] = expansion_tex[-1][:-1]

        expansion = MathTex(
            *expansion_tex
        ).scale(0.65).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT).shift([0, 0.15, 0])
        equals = MathTex("=").next_to(expansion[0], LEFT)
        self.play(first_term[0].animate.next_to(equals, LEFT), 
                  FadeOut(first_term[1]))
        
        self.play(Write(equals), Write(expansion))

        boxing = [Circumscribe(part) for part in expansion]
        
        self.play(AnimationGroup(*boxing[:2], lag_ratio=1.25))
        self.play(AnimationGroup(*boxing[2:], lag_ratio=0.15))

        new_expression = MathTex(r"\sum_{i=1}^{8}", "b_i(i-1)").match_x(b_k)
        self.play(ReplacementTransform(
            VGroup(first_term[0], equals, expansion), new_expression
        ))

        remove_sum = MathTex("b_i(i-1)").match_x(new_expression)
        self.play(TransformMatchingTex(new_expression, remove_sum))

        i_odd = MathTex(r"\underline{i\text{: } 1, 3, 5, 7 }"
                        ).next_to(remove_sum, UP, buff=1).scale(0.75)
        self.play(Write(i_odd))

        must_be_even = VGroup(
            # puts brace around the (i-1) part of the expression
            Brace(remove_sum[0][3:], buff=0.1, sharpness=1.5),
            Tex("must be even!")
        )
        must_be_even[1].next_to(must_be_even[0], DOWN)
        self.play(Create(must_be_even))

        is_even = MathTex(remove_sum.get_tex_string(), r"= \text{even}"
                          ).align_to(remove_sum, LEFT)
        self.play(TransformMatchingTex(remove_sum, is_even))

        mod_2 = MathTex(is_even[0].get_tex_string(), is_even[1].get_tex_string(), r"\pmod{2}"
                        ).match_x(is_even)
        self.play(TransformMatchingTex(is_even, mod_2),
                  Uncreate(must_be_even))

        equals_0 = MathTex(mod_2[0].get_tex_string(), "=0", mod_2[2].get_tex_string()
                           ).align_to(mod_2, LEFT)
        self.play(TransformMatchingTex(mod_2, equals_0))

        self.play(Unwrite(i_odd), TransformMatchingTex(equals_0, new_expression))

        i_even_label = MathTex(r"\underline{i \text{ even}}"
                               ).scale(0.75).next_to(new_expression[0][1], DOWN, buff=0.6
                                                     ).save_state()
        self.play(Write(i_even_label))
        self.play(Unwrite(i_even_label), TransformMatchingTex(new_expression, remove_sum))

        i_even = MathTex(r"\underline{i\text{: } 2, 4, 6, 8 }"
                        ).move_to(i_odd).scale(0.75)
        self.play(Write(i_even))
        
        must_be_odd = VGroup(
            # puts brace around the (i-1) part of the expression
            Brace(remove_sum[0][3:], buff=0.1, sharpness=1.5),
            Tex("must be odd!")
        )
        must_be_odd[1].next_to(must_be_odd[0], DOWN)
        self.play(Create(must_be_odd))

        mod_2 = MathTex(remove_sum.get_tex_string(), mod_2[2].get_tex_string()
                        ).match_x(is_even)
        self.play(TransformMatchingTex(remove_sum, mod_2),
                  Uncreate(must_be_odd))
        
        mod_2_temp = MathTex(
            mod_2[0].get_tex_string()[:mod_2[0].get_tex_string().index("(")],
            mod_2[0].get_tex_string()[mod_2[0].get_tex_string().index("("):],
            mod_2[1].get_tex_string()
        ).move_to(mod_2)
        self.play(ReplacementTransform(mod_2, mod_2_temp), run_time=0.01)
        mod_2 = mod_2_temp

        times_1 = MathTex(
            mod_2[0].get_tex_string(), "\cdot 1", mod_2[2].get_tex_string()
        ).move_to(mod_2)
        self.play(TransformMatchingTex(mod_2, times_1))

        remove_times_1 = MathTex(
            times_1[0].get_tex_string(), times_1[2].get_tex_string()
        ).align_to(times_1, LEFT)
        self.play(TransformMatchingTex(times_1, remove_times_1))

        final_expression = MathTex(
            new_expression[0].get_tex_string(),
            remove_times_1[0].get_tex_string()
        ).match_x(new_expression)
        i_even_label.restore().add_updater(
            lambda mob: mob.next_to(final_expression[0][1], DOWN, buff=0.6)
        )
        self.play(TransformMatchingTex(remove_times_1, final_expression),
                  Write(i_even_label), Unwrite(i_even))
        
        even_expansion = MathTex("= b_2 + b_4 + b_6 + b_8")
        self.play(
            Write(even_expansion),
            VGroup(final_expression, even_expansion
                   ).animate.arrange(RIGHT).match_x(new_expression)
        )
        even_expansion_box = SurroundingRectangle(even_expansion, buff=0.15, stroke_width=2)
        self.play(Create(even_expansion_box))

        self.play(FadeOut(b_k), FadeOut(i_and_j))
        
